from sqlmodel import Field, SQLModel
from typing import Optional
from enum import Enum
from datetime import date, time

class State(str, Enum):
    pendiente = "pendiente"
    confirmada = "confirmada"
    cancelada = "cancelada"


class Reservation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None,foreign_key="user.id")
    room_id: int = Field(default=None,foreign_key="room.id") 
    dates: date
    start_time:time
    end_time:time
    state: State = Field(default=State.pendiente)

