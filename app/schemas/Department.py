from pydantic import BaseModel
from typing import Optional, List

from app.schemas import Doctor

# Department schema (since Doctor has a relationship with Department)
class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class Department(DepartmentBase):
    id: int

    class Config:
        orm_mode = True
# Define a response model for a list of departments
class DepartmentListResponse(BaseModel):
    departments: List[Department]