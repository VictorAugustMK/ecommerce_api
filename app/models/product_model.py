from sqlalchemy import Column, Integer, Float, String, Boolean, Date, Text, DateTime, func
from app.db.base_class import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    barcode = Column(String, unique=True, nullable=False)
    section = Column(String, nullable=False)
    stock = Column(Integer, nullable=False)
    expiration_date = Column(Date, nullable=True)
    image_url = Column(String, nullable=True)
    available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())