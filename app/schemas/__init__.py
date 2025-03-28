# User schemas
from .user import User, UserCreate, UserUpdate, UserInDB

# Token schemas
from .token import Token, TokenData

# Patient schemas
from .Patient import Patient, PatientCreate, PatientUpdate, PatientWithUser,PatientRegistration

# Doctor schemas
from .Doctor import Doctor, DoctorCreate, DoctorUpdate, DoctorWithUser, DoctorRegistration

# Department schemas
from .Department import Department, DepartmentCreate, DepartmentUpdate

# Registration schemas
from .Department import Department, DepartmentCreate, DepartmentUpdate

# Login schema
from .Login import Login

from .Admin import Admin, AdminCreate, AdminUpdate, AdminWithUser, AdminRegistration