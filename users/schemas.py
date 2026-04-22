from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

# User Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
