from sqlalchemy import text
from sqlalchemy.orm import Session
from .. import schemas
from ..Oauth import security
from typing import Dict, Any


# User CRUD operations
def get_user_by_email(db: Session, email: str):
    query = text("SELECT * FROM users WHERE email = :email")
    result = db.execute(query, {"email": email}).first()
    return result


def get_user(db: Session, user_id: int):
    query = text("SELECT * FROM users WHERE id = :id")
    result = db.execute(query, {"id": user_id}).first()
    return result


def get_users(db: Session, skip: int = 0, limit: int = 100):
    query = text("SELECT * FROM users LIMIT :limit OFFSET :skip")
    result = db.execute(query, {"skip": skip, "limit": limit}).fetchall()
    return result


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    query = text("""
        INSERT INTO users (email, hashed_password, role)
        VALUES (:email, :hashed_password, :role)
    """)

    result = db.execute(
        query,
        {
            "email": user.email,
            "hashed_password": hashed_password,
            "role": user.role
        }
    )
    db.commit()

    # Get the created user ID
    last_id = result.lastrowid
    return get_user(db, last_id)


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not security.verify_password(password, user.hashed_password):
        return False
    return user


def update_user(db: Session, user_id: int, user_data: Dict[str, Any]):
    # First check if user exists
    user = get_user(db, user_id)
    if not user:
        return None

    # Prepare update parts
    update_parts = []
    params = {"id": user_id}

    for key, value in user_data.items():
        if key == "password":
            update_parts.append("hashed_password = :hashed_password")
            params["hashed_password"] = security.get_password_hash(value)
        elif key in ["email", "role"]:
            update_parts.append(f"{key} = :{key}")
            params[key] = value

    if not update_parts:
        return user

    # Build and execute update query
    query = text(f"""
        UPDATE users
        SET {', '.join(update_parts)}
        WHERE id = :id
    """)

    db.execute(query, params)
    db.commit()

    return get_user(db, user_id)


def delete_user(db: Session, user_id: int):
    # First get the user to return it
    user = get_user(db, user_id)
    if not user:
        return None

    # Delete the user
    query = text("DELETE FROM users WHERE id = :id")
    db.execute(query, {"id": user_id})
    db.commit()

    return user