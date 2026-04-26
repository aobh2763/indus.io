from typing import Generator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.core.permissions import GlobalRole
from app.core.security import decode_access_token
from app.db.database import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ── Database session ─────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Current user ─────────────────────────────────────────
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedError()

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise UnauthorizedError()

    from app.modules.identity.models import User

    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if user is None:
        raise UnauthorizedError()
    if not user.is_active:
        raise ForbiddenError(detail="Account is deactivated")
    return user


# ── Role-based access ───────────────────────────────────
def require_roles(*roles: GlobalRole):
    """Return a dependency that checks the user's global role."""

    def _checker(current_user=Depends(get_current_user)):
        if current_user.role not in [r.value for r in roles]:
            raise ForbiddenError(
                detail=f"Role '{current_user.role}' is not allowed. Required: {[r.value for r in roles]}"
            )
        return current_user

    return _checker
