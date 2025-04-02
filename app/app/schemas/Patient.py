from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

from app.schemas import User, UserCreate

# Patient schemas
class PatientBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    date_of_birth: date
    gender: str
    address: str
    avatar_url: str

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    avatar_url: Optional[str] = None

class Patient(PatientBase):
    patient_id: int

    class Config:
        orm_mode = True
        from_attributes = True

class PatientWithUser(Patient):
    user: Optional[User] = None

class PatientRegistration(BaseModel):
    user: UserCreate
    patient: PatientCreate
