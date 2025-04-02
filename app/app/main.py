from fastapi import FastAPI, Depends, HTTPException, status, Form, Query
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List, Optional

from app import crud, schemas
from app.Oauth import deps
from app.crud import patient as patient_crud
from app.crud import doctor as doctor_crud
from app.crud import admin as admin_crud
from app.crud import department as department_crud
from app.database import engine
from app.Oauth.security import create_access_token
from app.database.database import create_tables

# Create FastAPI instance
app = FastAPI()

create_tables()

# Authentication routes
@app.post("/login", response_model=schemas.Token)
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        role: str = Form(),
        db: Session = Depends(deps.get_db)
):
    user = crud.authenticate_user(db, email=form_data.username, password=form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.role != role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect role",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=deps.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Registration routes
@app.post("/register/patient", response_model=dict)
def register_patient(
        registration: schemas.PatientRegistration,
        db: Session = Depends(deps.get_db)
):
    # Check if user email already exists
    db_user = crud.get_user_by_email(db, email=registration.user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if patient email already exists
    db_patient = patient_crud.get_patient_by_email(db, email=registration.patient.email)
    if db_patient:
        raise HTTPException(status_code=400, detail="Email already registered as patient")

    # Set role to Patient for the user
    registration.user.role = "Patient"

    result = patient_crud.register_patient(db=db, registration=registration)

    # Convert row objects to dictionaries for jsonable_encoder
    user_dict = {column: getattr(result["user"], column) for column in result["user"]._mapping.keys()}
    patient_dict = {column: getattr(result["patient"], column) for column in result["patient"]._mapping.keys()}

    return {
        "user": jsonable_encoder(user_dict),
        "patient": jsonable_encoder(patient_dict)
    }


@app.post("/register/admin", response_model=dict)
def register_admin(
        registration: schemas.AdminRegistration,
        db: Session = Depends(deps.get_db)
):
    # Check if user email already exists
    db_user = crud.get_user_by_email(db, email=registration.user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if admin email already exists
    db_admin = admin_crud.get_admin_by_email(db, email=registration.user.email)
    if db_admin:
        raise HTTPException(status_code=400, detail="Email already registered as admin")

    # Set role to Admin for the user
    registration.user.role = "Admin"

    result = admin_crud.register_admin(db=db, registration=registration)

    # Convert row objects to dictionaries for jsonable_encoder
    user_dict = {column: getattr(result["user"], column) for column in result["user"]._mapping.keys()}
    admin_dict = {column: getattr(result["admin"], column) for column in result["admin"]._mapping.keys()}

    return {
        "user": jsonable_encoder(user_dict),
        "admin": jsonable_encoder(admin_dict)
    }

@app.post("/register/doctor", response_model=dict)
def register_doctor(
        registration: schemas.DoctorRegistration,
        db: Session = Depends(deps.get_db)
):
    # Check if user email already exists
    db_user = crud.get_user_by_email(db, email=registration.user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if doctor email already exists
    db_doctor = doctor_crud.get_doctor_by_email(db, email=registration.doctor.email)
    if db_doctor:
        raise HTTPException(status_code=400, detail="Email already registered as doctor")

    # Set role to Doctor for the user
    registration.user.role = "Doctor"

    result = doctor_crud.register_doctor(db=db, registration=registration)

    # Convert row objects to dictionaries for jsonable_encoder
    user_dict = {column: getattr(result["user"], column) for column in result["user"]._mapping.keys()}
    doctor_dict = {column: getattr(result["doctor"], column) for column in result["doctor"]._mapping.keys()}

    return {
        "user": jsonable_encoder(user_dict),
        "doctor": jsonable_encoder(doctor_dict)
    }


# User profile routes
@app.get("/me/patient", response_model=schemas.Patient)
def read_patient_me(
        current_user=Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    if current_user.role != "Patient":
        raise HTTPException(status_code=403, detail="Not a patient account")

    patient = patient_crud.get_patient_by_email(db, email=current_user.email)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    # Convert row object to dictionary that can be serialized
    patient_dict = {column: getattr(patient, column) for column in patient._mapping.keys()}
    return patient_dict


@app.get("/me/doctor", response_model=schemas.Doctor)
def read_doctor_me(
        current_user=Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    if current_user.role != "Doctor":
        raise HTTPException(status_code=403, detail="Not a doctor account")

    doctor = doctor_crud.get_doctor_by_email(db, email=current_user.email)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    # Convert row object to dictionary that can be serialized
    doctor_dict = {column: getattr(doctor, column) for column in doctor._mapping.keys()}
    return doctor_dict

@app.get("/me/admin", response_model=schemas.Admin)
def read_admin_me(
        current_user=Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):

    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not an admin account")

    admin = admin_crud.get_admin_by_email(db, email=current_user.email)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin profile not found")

    # Convert row object to dictionary that can be serialized
    admin_dict = {column: getattr(admin, column) for column in admin._mapping.keys()}

    return admin_dict

@app.get("/departments", response_model=List[schemas.Department])
async def get_departments(
        current_user=Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not an admin account")

    departments = department_crud.get_departments(db)
    return departments


@app.post("/doctors", response_model=List[schemas.Doctor])
async def get_doctors(
        current_user=Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db),
        department_id: str = Form(...)
):
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not an admin account")

    doctors = doctor_crud.get_doctors(db, department_id=department_id)

    return doctors if doctors else []  # Trả về danh sách rỗng thay vì None