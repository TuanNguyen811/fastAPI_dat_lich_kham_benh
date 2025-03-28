from sqlalchemy import text
from sqlalchemy.orm import Session
from .. import schemas
from typing import Optional, Dict, Any
from .user import create_user, get_user

# Doctor CRUD operations
def get_doctor_by_email(db: Session, email: str):
    query = text("SELECT * FROM doctors WHERE email = :email")
    result = db.execute(query, {"email": email}).first()
    return result

def get_doctor(db: Session, doctor_id: int):
    query = text("SELECT * FROM doctors WHERE id = :id")
    result = db.execute(query, {"id": doctor_id}).first()
    return result


from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.sql import text


def get_doctors(db: Session, skip: int = 0, limit: int = 100, department_id: Optional[int] = None) -> List[dict]:
    if department_id is not None:
        query = text("SELECT * FROM doctors WHERE department_id = :department_id LIMIT :limit OFFSET :skip")
        result = db.execute(query, {"department_id": department_id, "skip": skip, "limit": limit}).fetchall()

        doctors = [
            {"id": row[0], "email": row[1], "full_name": row[2], "phone": row[3], "birthdate": row[4],
             "department_id": row[5]}
            for row in result
        ]
        return doctors

    return []  # Trả về danh sách rỗng thay vì `None`


def create_doctor(db: Session, doctor: schemas.DoctorCreate, user_id: int):
    query = text("""
        INSERT INTO doctors (id, email, full_name, phone, birthdate, department_id)
        VALUES (:id, :email, :full_name, :phone, :birthdate, :department_id)
    """)

    db.execute(
        query,
        {
            "id": user_id,
            "email": doctor.email,
            "full_name": doctor.full_name,
            "phone": doctor.phone,
            "birthdate": doctor.birthdate,
            "department_id": doctor.department_id
        }
    )
    db.commit()

    return get_doctor(db, user_id)

def update_doctor(db: Session, doctor_id: int, doctor_data: Dict[str, Any]):
    # First check if doctor exists
    doctor = get_doctor(db, doctor_id)
    if not doctor:
        return None

    # Prepare update parts
    update_parts = []
    params = {"id": doctor_id}

    valid_fields = ["email", "full_name", "phone", "birthdate", "department_id"]

    for key, value in doctor_data.items():
        if key in valid_fields:
            update_parts.append(f"{key} = :{key}")
            params[key] = value

    if not update_parts:
        return doctor

    # Build and execute update query
    query = text(f"""
        UPDATE doctors
        SET {', '.join(update_parts)}
        WHERE id = :id
    """)

    db.execute(query, params)
    db.commit()

    return get_doctor(db, doctor_id)

def delete_doctor(db: Session, doctor_id: int):
    # First get the doctor to return it
    doctor = get_doctor(db, doctor_id)
    if not doctor:
        return None

    # Delete the doctor
    query = text("DELETE FROM doctors WHERE id = :id")
    db.execute(query, {"id": doctor_id})
    db.commit()

    return doctor

def register_doctor(db: Session, registration: schemas.DoctorRegistration):
    # Create user first
    user = create_user(db, registration.user)

    # Create doctor with user ID
    doctor = create_doctor(db, registration.doctor, user.id)

    return {"user": user, "doctor": doctor}