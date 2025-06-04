
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.services import user_service
from app.auth.services import jwt_service
from app.db.session import get_db
from app.schemas import UserResponse, UserCreate

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await user_service.create_user(user_data, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@auth_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await user_service.get_user_by_username(db, username=form_data.username)

    if not user or not user_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = jwt_service.create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/refresh-token")
async def refresh_token():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Funcionalidade não implementada")