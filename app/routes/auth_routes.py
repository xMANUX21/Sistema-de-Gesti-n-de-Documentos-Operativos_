from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session,select
from app.schemas.users.UsersSchema import UserCreate, UserLogin
from app.utils.dbConn import get_session
from app.auth.models.users.UsersModel import User
from app.auth.controllers.users.UsersController import register_controller, login_controller

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=User)
def register_user(user_data: UserCreate, session: Session = Depends(get_session)):
    return register_controller(user_data, session)

@router.post("/login")
def login(data: UserLogin, session: Session = Depends(get_session)):
    return login_controller(data, session)