# app/utils/dependencies.py
from fastapi import Depends
from app.utils.security import get_current_user_role
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def is_admin(token: str = Depends(oauth2_scheme)):
    role = get_current_user_role(token)
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador",
        )
    return True # True si la validación es exitosa


