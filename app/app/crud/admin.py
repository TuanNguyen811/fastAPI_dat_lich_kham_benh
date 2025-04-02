from sqlalchemy import text
from sqlalchemy.orm import Session
from .. import schemas
from typing import Dict, Any
from .user import create_user, get_user

# Admin CRUD operations
def get_admin_by_email(db: Session, email: str):
    query = text("SELECT * FROM Admins WHERE email = :email")
    result = db.execute(query, {"email": email}).first()
    return result

def get_admin(db: Session, admin_id: int):
    query = text("SELECT * FROM Admins WHERE admin_id = :admin_id")
    result = db.execute(query, {"admin_id": admin_id}).first()
    return result

def create_admin(db: Session, admin: schemas.AdminCreate, user_id: int):
    query = text("""
        INSERT INTO Admins (admin_id, email, full_name)
        VALUES (:admin_id, :email, :full_name)
    """)

    db.execute(
        query,
        {
            "admin_id": user_id,
            "email": admin.email,
            "full_name": admin.full_name
        }
    )
    db.commit()

    return get_admin(db, user_id)

def register_admin(db: Session, registration: schemas.AdminRegistration):
    # Create user first
    user = create_user(db, registration.user)

    # Create admin with user ID
    admin = create_admin(db, registration.admin, user.user_id)

    return {"user": user, "admin": admin}