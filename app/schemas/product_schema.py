from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import date

class ProductBase(BaseModel):
    description: str
    price: float
    barcode: str
    section: str
    stock: int
    expiration_date: Optional[date] = None
    image_url: Optional[str] = None
    available: Optional[bool] = True

    model_config = ConfigDict(from_attributes=True)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    description: Optional[str] = None
    price: Optional[float] = None
    barcode: Optional[str] = None
    section: Optional[str] = None
    stock: Optional[int] = None
    expiration_date: Optional[date] = None
    image_url: Optional[str] = None
    available: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("*", mode="before")
    @classmethod
    def at_least_one_field(cls, v, values, **kwargs):
        if not any(values.values()) and v is None:
            raise ValueError("Pelo menos um campo deve ser informado para atualização.")
        return v

class ProductOut(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
