from passlib.context import CryptContext
from fastapi import HTTPException
from sqlmodel import Session, select
from app.auth.models.users.UsersModel import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_user(session: Session, user_data):
    # Verificar si ya hay usuarios
    existing_users = session.exec(select(User)).all()

    # El primero será admin, los demás serán user
    assigned_role = "admin" if not existing_users else "user"

    # Validar email duplicado
    existing_email = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing_email:
        raise HTTPException(status_code=400, detail="Email ya registrado")

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hash_password(user_data.password),
        role=assigned_role
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    statement = select(User).where(User.email == email)  # <--- corregido
    result = session.exec(statement).first()
    if result and verify_password(password, result.password):
        return result
    return None
