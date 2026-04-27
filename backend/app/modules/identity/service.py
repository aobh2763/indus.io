import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.modules.identity.models import User
from app.modules.identity.schemas import UserRegister, UserUpdate


# ── Queries ──────────────────────────────────────────────
def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    return db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()


def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(User)
        .filter(User.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
        .all()
    )


# ── Commands ─────────────────────────────────────────────
def create_user(db: Session, data: UserRegister) -> User:
    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        role=data.role.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        return None
    # Update last_login
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: uuid.UUID, data: UserUpdate) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "role" and value is not None:
            setattr(user, field, value.value if hasattr(value, "value") else value)
        else:
            setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def soft_delete_user(db: Session, user_id: uuid.UUID) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return user
