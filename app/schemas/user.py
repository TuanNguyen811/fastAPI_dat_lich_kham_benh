from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional, List

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    role: str = Field(..., description="Role must be 'Patient' or 'Doctor'")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    id: int
    hashed_password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True