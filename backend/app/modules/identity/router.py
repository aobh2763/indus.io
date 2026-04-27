from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db, require_roles
from app.core.exceptions import (
    AlreadyExistsError,
    NotFoundError,
    UnauthorizedError,
)
from app.core.security import create_access_token
from app.core.permissions import GlobalRole
from app.modules.identity import service
from app.modules.identity.models import User
from app.modules.identity.schemas import (
    TokenResponse,
    UserRegister,
    UserResponse,
    UserUpdate,
)

router = APIRouter()


# ── Auth ─────────────────────────────────────────────────
@router.post("/auth/register", response_model=UserResponse, status_code=201, tags=["Auth"])
def register(data: UserRegister, db: Session = Depends(get_db)):
    if service.get_user_by_email(db, data.email):
        raise AlreadyExistsError("User with this email")
    return service.create_user(db, data)


@router.post("/auth/login", response_model=TokenResponse, tags=["Auth"])
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = service.authenticate_user(db, form.username, form.password)
    if not user:
        raise UnauthorizedError(detail="Invalid email or password")
    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return TokenResponse(access_token=token)


# ── Users CRUD ───────────────────────────────────────────
@router.get("/users/me", response_model=UserResponse, tags=["Users"])
def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users", response_model=list[UserResponse], tags=["Users"])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles(GlobalRole.ADMIN)),
):
    return service.get_all_users(db, skip, limit)


@router.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def get_user(user_id: str, db: Session = Depends(get_db), admin_user: User = Depends(require_roles(GlobalRole.ADMIN))):
    user = service.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError("User")
    return user


@router.put("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def update_user(
    user_id: str,
    data: UserUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles(GlobalRole.ADMIN)),
):
    user = service.update_user(db, user_id, data)
    if not user:
        raise NotFoundError("User")
    return user


@router.delete("/users/{user_id}", status_code=204, tags=["Users"])
def delete_user(user_id: str, db: Session = Depends(get_db), admin_user: User = Depends(require_roles(GlobalRole.ADMIN))):
    user = service.soft_delete_user(db, user_id)
    if not user:
        raise NotFoundError("User")
