from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

class ClientBase(BaseModel):
    name: str
    email: EmailStr
    cpf: str
    phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf: Optional[str] = None
    phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("*", mode="before")
    @classmethod
    def at_least_one_field(cls, v, values, **kwargs):
        if not any(values.values()) and v is None:
            raise ValueError("Pelo menos um campo deve ser informado para atualização.")
        return v

class ClientOut(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
