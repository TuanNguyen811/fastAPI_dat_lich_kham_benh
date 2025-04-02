from .user import get_user_by_email, create_user, authenticate_user
from .user import get_user_by_email, create_user, authenticate_user
from .doctor import get_doctor_by_email, get_doctor, get_doctors, create_doctor, update_doctor, delete_doctor, register_doctor
from .admin import get_admin_by_email, get_admin, create_admin, register_admin
from .department import get_department_by_name, get_department, get_departments, create_department, update_department, delete_department, get_departments
from .patient import get_patient_by_email, get_patient, get_patients, create_patient, update_patient, delete_patient, register_patient