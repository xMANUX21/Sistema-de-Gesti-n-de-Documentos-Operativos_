from sqlmodel import Field, SQLModel
from typing import Optional
from enum import Enum


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(index=True,unique=True)
    password: str
    role: Optional[str] = "user"  # sera "admin"  si es el primero