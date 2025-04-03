from fastapi import FastAPI, Depends, HTTPException, status, Form, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse, FileResponse

from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List, Optional, Dict, Any

import crud, schemas

from crud import *
from schemas import *
from Oauth import deps
from Oauth.security import create_access_token
from database.database import create_tables

import os
import uuid
import shutil

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

    # Extract role from the user dictionary
    user_role = user["role"]

    if user_role != role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect role",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=deps.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "role": user_role, "user_id": user["user_id"]},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


# Registration routes
@app.post("/register/patient", response_model=Dict[str, Any])
def register_patient(
        patient: schemas.PatientCreate,
        db: Session = Depends(deps.get_db),
):

    # Check if user with email already exists
    db_user = crud.get_user_by_email(db, email=patient.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Set role to Patient for the user
    patient.role = "Patient"

    # Create patient (this will create a user first and then a patient)
    result = crud.create_patient(db=db, patient=patient)

    if not result:
        raise HTTPException(status_code=500, detail="Failed to register patient")

    # Convert result to dict for response
    return {"message": "Patient registered successfully", "user_id": result[0]}


@app.post("/register/doctor", response_model=Dict[str, Any])
def register_doctor(
        doctor: schemas.DoctorCreate,
        db: Session = Depends(deps.get_db),
        current_user=Depends(deps.get_current_user)
):
    if current_user["role"] != "Admin":
        raise HTTPException(status_code=403, detail="Not an admin account")

    # Check if user with email already exists
    db_user = crud.get_user_by_email(db, email=doctor.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if department exists
    db_department = crud.get_department(db, department_id=doctor.department_id)
    if not db_department:
        raise HTTPException(status_code=404, detail="Department not found")

    # Set role to Doctor for the user
    doctor.role = "Doctor"

    # Create doctor (this will create a user first and then a doctor)
    result = crud.create_doctor(db=db, doctor=doctor)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to register doctor")

    # Convert result to dict for response
    return {"message": "Doctor registered successfully", "user_id": result[0]}


# User profile routes
@app.get("/me/patient", response_model=schemas.PatientResponse)
def read_patient_me(
        current_user=Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    if current_user["role"] != "Patient":
        raise HTTPException(status_code=403, detail="Not a patient account")

    patient = crud_patient.get_patient(db, patient_id=current_user["user_id"])

    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    # Convert row object to dictionary that can be serialized
    patient_dict = {column: getattr(patient, column) for column in patient._mapping.keys()}
    return patient_dict


@app.get("/me/doctor", response_model=schemas.DoctorResponse)
def read_doctor_me(
        current_user=Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    if current_user["role"] != "Doctor":
        raise HTTPException(status_code=403, detail="Not a doctor account")

    doctor = crud_doctor.get_doctor(db, doctor_id=current_user["user_id"])
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    # Convert row object to dictionary that can be serialized
    doctor_dict = {column: getattr(doctor, column) for column in doctor._mapping.keys()}
    return doctor_dict

@app.get("/me/admin", response_model=schemas.AdminResponse)
def read_admin_me(
        current_user=Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    if current_user["role"] != "Admin":
        raise HTTPException(status_code=403, detail="Not an admin account")

    admin = crud_admin.get_admin(db, admin_id=current_user["user_id"])
    if not admin:
        raise HTTPException(status_code=404, detail="Admin profile not found")

    # Convert row object to dictionary that can be serialized
    admin_dict = {column: getattr(admin, column) for column in admin._mapping.keys()}

    return admin_dict

# chưa làm update
@app.put("/me/update", response_model=Dict[str, Any])
def update_user_me(
        user_update: schemas.UserUpdate,
        current_user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    user_id = current_user.get("user_id")
    user_role = current_user.get("role")

    # Convert Pydantic model to dict and remove None values
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}

    # Update the user
    updated_user = crud.update_user(db, user_id=user_id, user_data=update_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User updated successfully"}


@app.put("/me/doctor/update", response_model=Dict[str, Any])
def update_doctor_me(
        doctor_update: schemas.DoctorUpdate,
        current_user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    if current_user.get("role") != "Doctor":
        raise HTTPException(status_code=403, detail="Not a doctor account")

    user_id = current_user.get("user_id")

    # Convert Pydantic model to dict and remove None values
    update_data = {k: v for k, v in doctor_update.dict().items() if v is not None}

    # Update the doctor
    updated_doctor = crud.update_doctor(db, doctor_id=user_id, doctor_data=update_data)
    if not updated_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return {"message": "Doctor updated successfully"}

@app.put("/me/patient/update", response_model=Dict[str, Any])
def update_patient_me(
        patient_update: schemas.PatientUpdate,
        current_user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    if current_user.get("role") != "Patient":
        raise HTTPException(status_code=403, detail="Not a patient account")

    user_id = current_user.get("user_id")

    # Convert Pydantic model to dict and remove None values
    update_data = {k: v for k, v in patient_update.dict().items() if v is not None}

    # Update the patient
    updated_patient = crud.update_patient(db, patient_id=user_id, patient_data=update_data)
    if not updated_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return {"message": "Patient updated successfully"}


# Department routes
@app.get("/departments", response_model=List[Dict[str, Any]])
def get_departments(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),

        current_user: Dict[str, Any] = Depends(deps.get_current_user)
):
    if current_user["role"] != "Admin":
        raise HTTPException(status_code=403, detail="Not an admin account")

    departments = crud.get_departments(db, skip=skip, limit=limit)
    return departments


@app.post("/departments", response_model=Dict[str, Any])
def create_department(
        department: schemas.DepartmentCreate,
        current_user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    if current_user.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Only admins can create departments")

    result = crud.create_department(db=db, department=department)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create department")

    return {"message": "Department created successfully", "department_id": result[0]}


@app.put("/departments/{department_id}", response_model=Dict[str, Any])
def update_department(
        department_id: int,
        department_update: schemas.DepartmentUpdate,
        current_user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    if current_user.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Only admins can update departments")

    # Convert Pydantic model to dict and remove None values
    update_data = {k: v for k, v in department_update.dict().items() if v is not None}

    # Update the department
    updated_department = crud.update_department(db, department_id=department_id, department_data=update_data)
    if not updated_department:
        raise HTTPException(status_code=404, detail="Department not found")

    return {"message": "Department updated successfully"}


@app.delete("/departments/{department_id}", response_model=Dict[str, Any])
def delete_department(
        department_id: int,
        current_user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    if current_user.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Only admins can delete departments")

    # Delete the department
    deleted_department = crud.delete_department(db, department_id=department_id)
    if not deleted_department:
        raise HTTPException(status_code=404, detail="Department not found")

    return {"message": "Department deleted successfully"}


# Doctor routes
@app.get("/doctors", response_model=List[Dict[str, Any]])
def get_doctors(
        skip: int = 0,
        limit: int = 100,
        department_id: Optional[int] = None,
        db: Session = Depends(deps.get_db)
):
    doctors = crud.get_doctors(db, skip=skip, limit=limit)

    # Filter by department_id if provided
    if department_id is not None:
        doctors = [d for d in doctors if d['department_id'] == department_id]

    return doctors


@app.get("/doctors/{doctor_id}", response_model=Dict[str, Any])
def get_doctor(
        doctor_id: int,
        db: Session = Depends(deps.get_db)
):
    doctor = crud.get_doctor(db, doctor_id=doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Convert row to dict
    doctor_dict = {
        "user_id": doctor[0],
        "email": doctor[1],
        "role": doctor[3],
        "full_name": doctor[4],
        "phone": doctor[5],
        "date_of_birth": doctor[6],
        "gender": doctor[7],
        "address": doctor[8],
        "avatar_url": doctor[9],
        "doctor_id": doctor[0],
        "department_id": doctor[10],
        "description": doctor[11]
    }

    return doctor_dict


# Patient routes
@app.get("/patients", response_model=List[Dict[str, Any]])
def get_patients(
        skip: int = 0,
        limit: int = 100,
        current_user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    if current_user.get("role") not in ["Admin", "Doctor"]:
        raise HTTPException(status_code=403, detail="Not authorized to view all patients")

    patients = crud.get_patients(db, skip=skip, limit=limit)
    return patients


@app.get("/patients/{patient_id}", response_model=Dict[str, Any])
def get_patient(
        patient_id: int,
        current_user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    # Check permissions
    if current_user.get("role") == "Patient" and current_user.get("user_id") != patient_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this patient")

    patient = crud.get_patient(db, patient_id=patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Convert row to dict
    patient_dict = {
        "user_id": patient[0],
        "email": patient[1],
        "role": patient[3],
        "full_name": patient[4],
        "phone": patient[5],
        "date_of_birth": patient[6],
        "gender": patient[7],
        "address": patient[8],
        "avatar_url": patient[9],
        "patient_id": patient[0],
        "insurance_id": patient[10]
    }

    return patient_dict


# Appointment routes
@app.post("/appointments", response_model=Dict[str, Any])
def create_appointment(
        appointment: schemas.AppointmentCreate,
        current_user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    # Check if patient exists
    patient = crud.get_patient(db, patient_id=appointment.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Check if doctor exists
    doctor = crud.get_doctor(db, doctor_id=appointment.doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Check if department exists
    department = crud.get_department(db, department_id=appointment.department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    # Create appointment
    result = crud.create_appointment(db=db, appointment=appointment)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create appointment")

    return {"message": "Appointment created successfully", "appointment_id": result[0]}


@app.get("/appointments", response_model=List[Dict[str, Any]])
def get_appointments(
        skip: int = 0,
        limit: int = 100,
        patient_id: Optional[int] = None,
        doctor_id: Optional[int] = None,
        current_user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    appointments = crud.get_appointments(db, skip=skip, limit=limit)

    # Filter by patient_id or doctor_id if provided
    if patient_id is not None:
        appointments = [a for a in appointments if a['patient_id'] == patient_id]

    if doctor_id is not None:
        appointments = [a for a in appointments if a['doctor_id'] == doctor_id]

    # Apply access control
    user_role = current_user.get("role")
    user_id = current_user.get("user_id")

    if user_role == "Patient":
        # Patients can only see their own appointments
        appointments = [a for a in appointments if a['patient_id'] == user_id]
    elif user_role == "Doctor":
        # Doctors can only see appointments they are assigned to
        appointments = [a for a in appointments if a['doctor_id'] == user_id]

    return appointments


@app.get("/appointments/{appointment_id}", response_model=Dict[str, Any])
def get_appointment(
        appointment_id: int,
        current_user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    appointment = crud.get_appointment(db, appointment_id=appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Convert row to dict
    appointment_dict = {
        "appointment_id": appointment[0],
        "patient_id": appointment[1],
        "doctor_id": appointment[2],
        "department_id": appointment[3],
        "appointment_date": appointment[4],
        "shift": appointment[5],
        "description": appointment[6],
        "status": appointment[7],
        "created_at": appointment[8]
    }

    # Apply access control
    user_role = current_user.get("role")
    user_id = current_user.get("user_id")

    if (user_role == "Patient" and appointment_dict["patient_id"] != user_id) or \
            (user_role == "Doctor" and appointment_dict["doctor_id"] != user_id):
        raise HTTPException(status_code=403, detail="Not authorized to view this appointment")

    return appointment_dict


@app.put("/appointments/{appointment_id}", response_model=Dict[str, Any])
def update_appointment(
        appointment_id: int,
        appointment_update: schemas.AppointmentUpdate,
        current_user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    # Check if appointment exists
    appointment = crud.get_appointment(db, appointment_id=appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Apply access control
    user_role = current_user.get("role")
    user_id = current_user.get("user_id")

    if user_role == "Patient" and appointment[1] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this appointment")
    elif user_role == "Doctor" and appointment[2] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this appointment")

    # Convert Pydantic model to dict and remove None values
    update_data = {k: v for k, v in appointment_update.dict().items() if v is not None}

    # Update the appointment
    updated_appointment = crud.update_appointment(db, appointment_id=appointment_id, appointment_data=update_data)
    if not updated_appointment:
        raise HTTPException(status_code=500, detail="Failed to update appointment")

    return {"message": "Appointment updated successfully"}


# Create upload directories if they don't exist
UPLOAD_DIR = "uploads"
AVATAR_DIR = os.path.join(UPLOAD_DIR, "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)


@app.post("/me/avatar", status_code=status.HTTP_200_OK)
async def upload_avatar(
        file: UploadFile = File(...),
        current_user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    user_id = current_user.get("user_id")
    user_role = current_user.get("role")

    # Process file upload
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(AVATAR_DIR, filename)

    # Save file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Update user avatar
    avatar_url = f"/avatars/{filename}"

    # Update the appropriate record based on role
    if user_role == "Doctor":
        update_data = {"avatar_url": avatar_url}
        user = crud.update_user(db, user_id=user_id, user_data=update_data)
    elif user_role == "Patient":
        update_data = {"avatar_url": avatar_url}
        user = crud.update_user(db, user_id=user_id, user_data=update_data)
    elif user_role == "Admin":
        update_data = {"avatar_url": avatar_url}
        user = crud.update_user(db, user_id=user_id, user_data=update_data)
    else:
        raise HTTPException(status_code=400, detail="Invalid user role")

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"filename": filename, "avatar_url": avatar_url}


@app.get("/avatars/{filename}")
async def get_avatar(filename: str):
    file_path = os.path.join(AVATAR_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Avatar not found")

    return FileResponse(file_path)


# Health metrics routes
@app.post("/health-metrics", response_model=Dict[str, Any])
def create_health_metric(
        metric: schemas.PatientHealthMetricsCreate,
        current_user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    # Check permissions
    if current_user.get("role") == "Patient" and current_user.get("user_id") != metric.patient_id:
        raise HTTPException(status_code=403, detail="Not authorized to create metrics for this patient")

    # Check if patient exists
    patient = crud.get_patient(db, patient_id=metric.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Create health metric
    result = crud.create_patient_health_metric(db=db, metric=metric)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create health metric")

    return {"message": "Health metric created successfully", "metric_id": result[0]}


@app.get("/health-metrics", response_model=List[Dict[str, Any]])
def get_health_metrics(
        skip: int = 0,
        limit: int = 100,
        patient_id: Optional[int] = None,
        current_user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    # Apply access control
    user_role = current_user.get("role")
    user_id = current_user.get("user_id")

    if user_role == "Patient":
        # Patients can only see their own metrics
        patient_id = user_id

    metrics = crud.get_patient_health_metrics(db, patient_id=patient_id, skip=skip, limit=limit)
    return metrics


# Medical history routes
@app.post("/medical-history", response_model=Dict[str, Any])
def create_medical_history(
        history: schemas.MedicalHistoryCreate,
        current_user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    # Only doctors can create medical history
    if current_user.get("role") != "Doctor":
        raise HTTPException(status_code=403, detail="Only doctors can create medical history records")

    # Check if the doctor is the one assigned to the appointment
    appointment = crud.get_appointment(db, appointment_id=history.appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment[2] != current_user.get("user_id"):
        raise HTTPException(status_code=403,
                            detail="You are not authorized to create medical history for this appointment")

    # Create medical history
    result = crud.create_medical_history(db=db, history=history)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create medical history")

    return {"message": "Medical history created successfully", "history_id": result[0]}


@app.get("/medical-history", response_model=List[Dict[str, Any]])
def get_medical_histories(
        skip: int = 0,
        limit: int = 100,
        patient_id: Optional[int] = None,
        current_user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    # Apply access control
    user_role = current_user.get("role")
    user_id = current_user.get("user_id")

    if user_role == "Patient":
        # Patients can only see their own medical history
        patient_id = user_id

    histories = crud.get_medical_histories(db, patient_id=patient_id, skip=skip, limit=limit)

    if user_role == "Doctor":
        # Doctors can only see medical histories they created
        histories = [h for h in histories if h['doctor_id'] == user_id]

    return histories


@app.get("/medical-history/{history_id}", response_model=Dict[str, Any])
def get_medical_history(
        history_id: int,
        current_user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    history = crud.get_medical_history(db, history_id=history_id)
    if not history:
        raise HTTPException(status_code=404, detail="Medical history not found")

    # Convert row to dict
    history_dict = {
        "history_id": history[0],
        "appointment_id": history[1],
        "patient_id": history[2],
        "doctor_id": history[3],
        "department_id": history[4],
        "visit_date": history[5],
        "diagnosis": history[6],
        "treatment": history[7],
        "notes": history[8],
        "created_at": history[9]
    }

    # Apply access control
    user_role = current_user.get("role")
    user_id = current_user.get("user_id")

    if (user_role == "Patient" and history_dict["patient_id"] != user_id) or \
            (user_role == "Doctor" and history_dict["doctor_id"] != user_id):
        raise HTTPException(status_code=403, detail="Not authorized to view this medical history")

    return history_dict


# Notification routes
@app.post("/notifications", response_model=Dict[str, Any])
def create_notification(
        notification: schemas.NotificationCreate,
        current_user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    # Only admins and doctors can create notifications
    if current_user.get("role") not in ["Admin", "Doctor"]:
        raise HTTPException(status_code=403, detail="Not authorized to create notifications")

    # Check if the user exists
    user = crud.get_user(db, user_id=notification.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create notification
    result = crud.create_notification(db=db, notification=notification)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create notification")

    return {"message": "Notification created successfully", "notification_id": result[0]}


@app.get("/notifications", response_model=List[Dict[str, Any]])
def get_notifications(
        skip: int = 0,
        limit: int = 100,
        current_user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    # Users can only see their own notifications
    user_id = current_user.get("user_id")

    notifications = crud.get_notifications(db, user_id=user_id, skip=skip, limit=limit)
    return notifications