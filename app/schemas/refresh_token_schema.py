from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class RefreshTokenOut(BaseModel):
    id: int
    user_id: UUID
    token: str
    expires_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TokenPayload(BaseModel):
    sub: str
    role: str
    exp: int
    jti: str

    model_config = ConfigDict(from_attributes=True)