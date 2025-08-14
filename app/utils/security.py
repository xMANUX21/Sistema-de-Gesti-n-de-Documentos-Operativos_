from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from app.schemas.users.UsersSchema import UserCreate,UserLogin ,UserResponse
import os
from fastapi import HTTPException ,status ,Depends
from .dbConn import get_db_connection
from fastapi.security import OAuth2PasswordBearer
import mysql.connector
from passlib.context import CryptContext
import bcrypt

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

SECRET_KEY= os.getenv('SECRET_KEY')
ALGORITHM= os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES',30))

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

#Hashea el token antes de guardarlo en la base de datos.
def hash_token(token: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(token.encode('utf-8'), salt).decode('utf-8')


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user_role(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de acceso inválido",
            )
        return role
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar el token",
        )
    

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db_connection: mysql.connector.MySQLConnection = Depends(get_db_connection)
) -> UserResponse:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de acceso inválido"
            )
        
        # Buscar al usuario en la base de datos por su ID
        cursor = db_connection.cursor(dictionary=True)
        sql_select = "SELECT id, name, email, role, department FROM users WHERE id = %s"
        cursor.execute(sql_select, (user_id,))
        user_data = cursor.fetchone()
        cursor.close()

        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado"
            )

        # Devolver el objeto UserResponse (el modelo de pydantic)
        return UserResponse(**user_data)
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar el token"
        )