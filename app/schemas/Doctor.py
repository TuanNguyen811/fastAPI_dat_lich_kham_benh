from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
from app.schemas import User, UserCreate


# Doctor schemas
class DoctorBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    birthdate: date
    department_id: Optional[int] = None

class DoctorCreate(DoctorBase):
    pass

class DoctorUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birthdate: Optional[date] = None
    department_id: Optional[int] = None
    password: Optional[str] = None

class Doctor(DoctorBase):
    id: int

    class Config:
        orm_mode = True

class DoctorWithUser(Doctor):
    user: Optional[User] = None

class DoctorRegistration(BaseModel):
    user: UserCreate
    doctor: DoctorCreate