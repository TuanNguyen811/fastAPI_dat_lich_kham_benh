from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
from app.schemas import User, UserCreate


# Doctor schemas
class DoctorBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    date_of_birth: date
    gender: str
    address: str
    description: Optional[int] = None
    avatar_url: Optional[int] = None
    department_id: Optional[int] = None

class DoctorCreate(DoctorBase):
    pass

class DoctorUpdate(BaseModel):
    full_name: Optional[int] = None
    email: Optional[EmailStr] = None
    phone: Optional[int] = None
    date_of_birth: Optional[date] = None
    gender: Optional[int] = None
    address: Optional[int] = None
    description: Optional[int] = None
    avatar_url: Optional[int] = None
    department_id: Optional[int] = None

class Doctor(DoctorBase):
    doctor_id: int

    class Config:
        orm_mode = True

class DoctorWithUser(Doctor):
    user: Optional[User] = None

class DoctorRegistration(BaseModel):
    user: UserCreate
    doctor: DoctorCreate