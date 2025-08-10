from pydantic import BaseModel
from enum import Enum
from sqlmodel import Field, SQLModel
from typing import Optional

# class Role(str, Enum):
#     admin = "admin"
#     user = "user"
  
class UserCreate(SQLModel):
    name: str
    email: str
    password: str
    # role: Optional[Role] = None  # Lo dejamos opcional


class UserLogin(BaseModel):
    email: str
    password: str
