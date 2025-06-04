from sqlalchemy import Column, String
from sqlalchemy.orm import mapped_column, Mapped
from app.db.base_class import Base

class UserLogin(Base):
    __tablename__ = "user_login"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)