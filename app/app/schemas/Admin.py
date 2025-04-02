from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional, List
from app.schemas import User, UserCreate

# Patient schemas
class AdminBase(BaseModel):
    full_name: str
    email: EmailStr

class AdminCreate(AdminBase):
    pass

class AdminUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class Admin(AdminBase):
    admin_id: int

    class Config:
        orm_mode = True
        from_attributes = True

class AdminWithUser(Admin):
    user: Optional[User] = None

class AdminRegistration(BaseModel):
    user: UserCreate
    admin: AdminCreate
