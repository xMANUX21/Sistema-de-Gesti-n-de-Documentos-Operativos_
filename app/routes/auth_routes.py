from fastapi import APIRouter, HTTPException, Depends ,status ,Body
from app.schemas.users.UsersSchema import UserCreate, UserLogin ,UserResponse ,ResetPassword
from app.utils.dbConn import get_db_connection
import mysql.connector
from passlib.hash import bcrypt
from typing import Annotated
from  app.auth.controllers.users.UsersController import increase_failed_attempts
from app.utils.security import create_access_token,hash_password,verify_password ,hash_token
from app.auth.controllers.users.UsersController import assign_role_based_on_count
from app.utils.dependencies import is_admin
from app.utils.emailUtils import send_reset_password_email
import uuid
from datetime import datetime ,timedelta
from dotenv import load_dotenv
import os
import bcrypt

load_dotenv()

db_host = os.getenv('HOST_DB')
front_port = os.getenv('FRONT_PORT') # Variable del puerto



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
        sql_insert = "INSERT INTO users (name, email, password_hash, role, department) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql_insert, (user_data.name, user_data.email, hashed_password, assigned_role, user_data.department))
        db_connection.commit()
        
        # 5. Obtener los datos del usuario recien creado para la respuesta
        last_id = cursor.lastrowid
        sql_select_new_user = "SELECT id, name, email, role, department FROM users WHERE id = %s"
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
        sql_select = "SELECT id, email, password_hash, role, is_locked, failed_attempts ,name FROM users WHERE email = %s"
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
            "role": user_db["role"],
            "email": user_db["email"],
            "name": user_db["name"]
        }
        token = create_access_token(token_payload)
        
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        db_connection.rollback()
        raise e
    finally:
        cursor.close()





@router.post("/forgot-password")
def forgot_password(email: str = Body(..., embed=True), db_connection: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    cursor = db_connection.cursor(dictionary=True) # <-- Cambiar a dictionary=True para obtener un dict
    try:
        # Buscar usuario por email y obtener su info completa
        sql_select = "SELECT id, name, email FROM users WHERE email = %s"
        cursor.execute(sql_select, (email,))
        user_info = cursor.fetchone() #  user_info ahora es un diccionario

        if not user_info:
            return {"message": "Si el email existe, se ha enviado un enlace para restablecer la contraseña."}
        
        user_id = user_info['id'] #  Accede al ID correctamente

        #  para generar y guardar el token 
        raw_token = str(uuid.uuid4())
        hashed_token = hash_token(raw_token)
        expires_at = datetime.now() + timedelta(minutes=15)
        
        sql_insert = "INSERT INTO password_reset_tokens (user_id, token_hash, expires_at) VALUES (%s, %s, %s)"
        cursor.execute(sql_insert, (user_id, hashed_token, expires_at))
        db_connection.commit()

        # Enviar el email con el token SIN HASHEAR
        reset_link = f"http://{db_host}:{front_port}/reset-password?token={raw_token}"
        send_reset_password_email(user_info, reset_link) #  Pasa el diccionario user_info

        return {"message": " Se ha enviado un enlace al email, para restablecer la contraseña."}
    except Exception as e:
        db_connection.rollback()
        raise e
    finally:
        cursor.close()



@router.post("/reset-password")
def reset_password(data: ResetPassword, db_connection: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    cursor = db_connection.cursor(dictionary=True) # Usamos dictionary=True para facilitar
    try:
        # 1. Buscar todos los tokens que sean validos (no usados y no expirados)
        sql_select = "SELECT user_id, token_hash, expires_at FROM password_reset_tokens WHERE used_at IS NULL AND expires_at > NOW()"
        cursor.execute(sql_select)
        possible_tokens = cursor.fetchall()
        
        found_token = None
        
        # 2. Iterar sobre ellos y verificar la coincidencia con bcrypt.checkpw
        for token_record in possible_tokens:
            if bcrypt.checkpw(data.token.encode('utf-8'), token_record['token_hash'].encode('utf-8')):
                found_token = token_record
                break
        
        if not found_token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido o ya usado.")
        
        user_id = found_token['user_id']

        # 3. Hashear la nueva contraseña
        hashed_password = hash_password(data.password)
        
        # 4. Actualizar la contraseña del usuario
        sql_update_password = "UPDATE users SET password_hash = %s WHERE id = %s"
        cursor.execute(sql_update_password, (hashed_password, user_id))
        
        # 5. Marcar el token como usado
        sql_update_token = "UPDATE password_reset_tokens SET used_at = %s WHERE user_id = %s AND token_hash = %s"
        cursor.execute(sql_update_token, (datetime.now(), user_id, found_token['token_hash']))
        
        db_connection.commit()
        
        return {"message": "Contraseña restablecida con éxito."}
    except Exception as e:
        db_connection.rollback()
        raise e
    finally:
        cursor.close()