from fastapi import Depends, HTTPException
from sqlmodel import Session, select
from app.auth.service import create_user, authenticate_user
from app.schemas.users.UsersSchema import UserCreate, UserLogin
from app.utils.dbConn import get_session
from app.utils.security import create_access_token
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.auth.models.users.UsersModel import User
from app.utils.security import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def register_controller(user_data: UserCreate, session: Session):
    return create_user(session, user_data)


def login_controller(data: UserLogin, session: Session):
    user = authenticate_user(session, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        raise credentials_exception
    return user
