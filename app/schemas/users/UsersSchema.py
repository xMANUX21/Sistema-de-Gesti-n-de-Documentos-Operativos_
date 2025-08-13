from pydantic import BaseModel
from enum import Enum
from sqlmodel import Field, SQLModel
from typing import Optional

# class Role(str, Enum):
#     admin = "admin"
#     user = "user"

class UserLogin(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    department: Optional[str]=None
    
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str