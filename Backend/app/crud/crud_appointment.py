from sqlalchemy import text
from sqlalchemy.orm import Session

import schemas
import crud

from typing import Optional, Dict, Any, List


# Appointment CRUD operations
def get_appointment(db: Session, appointment_id: int):
    query = text("SELECT * FROM Appointments WHERE appointment_id = :appointment_id")
    result = db.execute(query, {"appointment_id": appointment_id}).first()
    return result


def get_appointments(db: Session, skip: int = 0, limit: int = 100) -> List[dict]:
    query = text("SELECT * FROM Appointments LIMIT :limit OFFSET :skip")
    result = db.execute(query, {"skip": skip, "limit": limit}).fetchall()

    appointments = [
        {
            "appointment_id": row[0],
            "patient_id": row[1],
            "doctor_id": row[2],
            "department_id": row[3],
            "appointment_date": row[4],
            "shift": row[5],
            "description": row[6],
            "status": row[7],
            "created_at": row[8]
        } for row in result
    ]

    return appointments


def create_appointment(db: Session, appointment: schemas.AppointmentCreate):
    query = text("""
        INSERT INTO Appointments (patient_id, doctor_id, department_id, appointment_date, shift, description)
        VALUES (:patient_id, :doctor_id, :department_id, :appointment_date, :shift, :description)
    """)

    db.execute(
        query,
        {
            "patient_id": appointment.patient_id,
            "doctor_id": appointment.doctor_id,
            "department_id": appointment.department_id,
            "appointment_date": appointment.appointment_date,
            "shift": appointment.shift,
            "description": appointment.description
        }
    )
    db.commit()

    # Get the last inserted ID
    result = db.execute(text("SELECT LAST_INSERT_ID()")).scalar()

    return get_appointment(db, result)


def update_appointment(db: Session, appointment_id: int, appointment_data: Dict[str, Any]):
    # First check if appointment exists
    appointment = get_appointment(db, appointment_id)
    if not appointment:
        return None

    # Prepare update parts
    update_parts = []
    params = {"appointment_id": appointment_id}

    valid_fields = ["appointment_date", "shift", "description", "status"]

    for key, value in appointment_data.items():
        if key in valid_fields:
            update_parts.append(f"{key} = :{key}")
            params[key] = value

    if not update_parts:
        return appointment

    # Build and execute update query
    query = text(f"""
        UPDATE Appointments
        SET {', '.join(update_parts)}
        WHERE appointment_id = :appointment_id
    """)

    db.execute(query, params)
    db.commit()

    return get_appointment(db, appointment_id)


def delete_appointment(db: Session, appointment_id: int):
    # First get the appointment to return it
    appointment = get_appointment(db, appointment_id)
    if not appointment:
        return None

    # Delete the appointment
    query = text("DELETE FROM Appointments WHERE appointment_id = :appointment_id")
    db.execute(query, {"appointment_id": appointment_id})
    db.commit()

    return appointment