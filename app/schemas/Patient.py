from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

from app.schemas import User, UserCreate


# Patient schemas
class PatientBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    birthdate: date
    gender: str
    address: str

class PatientCreate(PatientBase):
    pass
class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birthdate: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    password: Optional[str] = None

class Patient(PatientBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True

class PatientWithUser(Patient):
    user: Optional[User] = None

class PatientRegistration(BaseModel):
    user: UserCreate
    patient: PatientCreate
