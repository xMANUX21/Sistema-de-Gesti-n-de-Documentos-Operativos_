from fastapi import APIRouter, HTTPException, Depends ,status ,Body
from app.schemas.users.UsersSchema import UserCreate, UserLogin ,UserResponse
from app.utils.dbConn import get_db_connection
import mysql.connector
from passlib.hash import bcrypt
from typing import Annotated
from  app.auth.controllers.users.UsersController import increase_failed_attempts
from app.utils.security import create_access_token,hash_password,verify_password
from app.auth.controllers.users.UsersController import assign_role_based_on_count
from app.utils.dependencies import is_admin

router = APIRouter(tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED , dependencies=[Depends(is_admin)])
def register_user(user_data: UserCreate = Body(...), db_connection: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    cursor = db_connection.cursor(dictionary=True)
    
    try:
        # 1. Verificar si el email ya existe
        sql_check = "SELECT id FROM users WHERE email = %s"
        cursor.execute(sql_check, (user_data.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        # 2. Asignar el rol de forma dinamica
        assigned_role = assign_role_based_on_count(db_connection)

        # 3. Hashear la contraseña de forma segura
        hashed_password = hash_password(user_data.password)

        # 4. Insertar el nuevo usuario en la base de datos
        sql_insert = "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_insert, (user_data.name, user_data.email, hashed_password, assigned_role))
        db_connection.commit()
        
        # 5. Obtener los datos del usuario recien creado para la respuesta
        last_id = cursor.lastrowid
        sql_select_new_user = "SELECT id, name, email, role FROM users WHERE id = %s"
        cursor.execute(sql_select_new_user, (last_id,))
        new_user_db_data = cursor.fetchone()
        
        if not new_user_db_data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo recuperar los datos del nuevo usuario.")

        return UserResponse(**new_user_db_data)
    except Exception as e:
        db_connection.rollback()
        raise e
    finally:
        cursor.close()


# app/routes/auth_routes.py
@router.post("/login")
def login(data: UserLogin, db_connection: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    cursor = db_connection.cursor(dictionary=True)
    
    try:
        # 1. Buscar usuario por email y obtener los campos de bloqueo
        sql_select = "SELECT id, email, password_hash, role, is_locked, failed_attempts FROM users WHERE email = %s"
        cursor.execute(sql_select, (data.email,))
        user_db = cursor.fetchone()
        # 2. Verificar si el usuario existe
        if not user_db:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")

        # Verificar si la cuenta está bloqueada
        if user_db["is_locked"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="La cuenta está bloqueada. Por favor, contacta a soporte.")
         # 4. Verificar la contraseña
        if not verify_password(data.password, user_db["password_hash"]):
             # Si la contraseña es incorrecta, aumentan los intentos fallidos
            increase_failed_attempts(db_connection, user_db["id"])
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
        
        # Generar y devolver el token JWT (aquí no hay reseteo)
        token_payload = {
            "sub": str(user_db["id"]),
            "role": user_db["role"]
        }
        token = create_access_token(token_payload)
        
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        db_connection.rollback()
        raise e
    finally:
        cursor.close()
