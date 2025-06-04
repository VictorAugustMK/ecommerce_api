
from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.services.user_service import create_user
from app.db import get_db
from app.schemas import UserResponse, UserCreate

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/login")
async def login():
    return {"message": "Login (mock)"}

@auth_router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(user_data, db)

@auth_router.post("/refresh-token")
async def refresh_token():
    return {"message": "Refresh token (mock)"}
