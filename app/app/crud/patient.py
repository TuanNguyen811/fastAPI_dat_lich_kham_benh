from sqlalchemy import text
from sqlalchemy.orm import Session
from .. import schemas
from typing import Dict, Any
from .user import create_user, get_user


# Patient CRUD operations
def get_patient_by_email(db: Session, email: str):
    query = text("SELECT * FROM Patients WHERE email = :email")
    result = db.execute(query, {"email": email}).first()
    return result

def get_patient(db: Session, patient_id: int):
    query = text("SELECT * FROM Patients WHERE patient_id = :id")
    result = db.execute(query, {"id": patient_id}).first()
    return result


def get_patients(db: Session, skip: int = 0, limit: int = 100):
    query = text("SELECT * FROM Patients LIMIT :limit OFFSET :skip")
    result = db.execute(query, {"skip": skip, "limit": limit}).fetchall()
    return result


def create_patient(db: Session, patient: schemas.PatientCreate, user_id: int):
    query = text("""
        INSERT INTO Patients (patient_id, full_name, email, phone, date_of_birth, gender, address, avatar_url)
        VALUES (:id, :full_name, :email, :phone, :birthdate, :gender, :address, :avatar_url)
    """)

    db.execute(
        query,
        {
            "id": user_id,
            "full_name": patient.full_name,
            "email": patient.email,
            "phone": patient.phone,
            "birthdate": patient.date_of_birth,
            "gender": patient.gender,
            "address": patient.address,
            "avatar_url": patient.avatar_url
        }
    )
    db.commit()

    return get_patient(db, user_id)


def update_patient(db: Session, patient_id: int, patient_data: Dict[str, Any]):
    # First check if patient exists
    patient = get_patient(db, patient_id)
    if not patient:
        return None

    # Prepare update parts
    update_parts = []
    params = {"id": patient_id}

    valid_fields = ["full_name", "email", "phone", "date_of_birth", "gender", "address", "avatar_url"]

    for key, value in patient_data.items():
        if key in valid_fields:
            update_parts.append(f"{key} = :{key}")
            params[key] = value

    if not update_parts:
        return patient

    # Build and execute update query
    query = text(f"""
        UPDATE Patients
        SET {', '.join(update_parts)}
        WHERE patient_id = :id
    """)

    db.execute(query, params)
    db.commit()

    return get_patient(db, patient_id)


def delete_patient(db: Session, patient_id: int):
    # First get the patient to return it
    patient = get_patient(db, patient_id)
    if not patient:
        return None

    # Delete the patient
    query = text("DELETE FROM Patients WHERE patient_id = :id")
    db.execute(query, {"id": patient_id})
    db.commit()

    return patient


def register_patient(db: Session, registration: schemas.PatientRegistration):
    # Create user first
    user = create_user(db, registration.user)

    # Create patient with the user's ID
    patient = create_patient(db, registration.patient, user.id)

    return {"user": user, "patient": patient}