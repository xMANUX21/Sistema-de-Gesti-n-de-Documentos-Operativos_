from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session,select
from app.utils.dbConn import session_dep
from app.utils.dbConn import get_session
from app.auth.models.users.UsersModel import User
from app.auth.controllers.users.UsersController import get_current_user

router = APIRouter(tags=["users"])


#El login y register estan en auth Routes

#Optener el usuario actual
@router.get("/me", response_model=User)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


#Optener usuarios solo admin
@router.get("/", response_model=list[User])
def get_all_users(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo los administradores pueden ver todos los usuarios")
    users = session.exec(select(User)).all()
    return users


#Borrar un usuario solo admin
@router.delete("/{id}", status_code=204)
def delete_user(id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo los administradores pueden eliminar usuarios")
    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    session.delete(user)
    session.commit()
