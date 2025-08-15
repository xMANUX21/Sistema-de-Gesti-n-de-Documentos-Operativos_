from fastapi import Depends, HTTPException
from app.schemas.users.UsersSchema import UserCreate, UserLogin
from app.utils.dbConn import get_db_connection
from app.utils.security import create_access_token
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.utils.security import SECRET_KEY, ALGORITHM
from app.utils.emailUtils import send_unlock_email
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

db_host = os.getenv('HOST_DB')
front_port = os.getenv('FRONT_PORT') # Variable del puerto

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

#Ahora sirve para asignar el role operador , ya que hay un admin predeterminado
def assign_role_based_on_count(db_connection: mysql.connector.MySQLConnection) -> str:
    cursor = db_connection.cursor()
    try:
        # Contar el número de usuarios en la tabla 'users'
        sql_count = "SELECT COUNT(*) FROM users"
        cursor.execute(sql_count)
        user_count = cursor.fetchone()[0]

        # Si el conteo es 0, el rol es admin, si no, es operador
        if user_count == 0:
            return "admin"
        else:
            return "operador"
    except Exception as e:
        print(f"Error al contar usuarios: {e}")
        # En caso de error, se asigna operador para mayor seguridad
        return "operador"
    finally:
        cursor.close()


 # Aumenta el contador de intentos fallidos para un usuario. Si excede un limite bloquea la cuenta.
# Aumenta el contador de intentos fallidos para un usuario,si no es un admin.
def increase_failed_attempts(db_connection: mysql.connector.MySQLConnection, user_id: int):
    cursor = db_connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, name, email, role, failed_attempts FROM users WHERE id = %s", (user_id,))
        user_info = cursor.fetchone()
        
        if not user_info or user_info["role"] == "admin":
            return
            
        new_attempts = user_info["failed_attempts"] + 1
        
        if new_attempts >= 5:
            sql_update = "UPDATE users SET failed_attempts = %s, is_locked = TRUE WHERE id = %s"
            cursor.execute(sql_update, (new_attempts, user_id))
            
            # --- Enviar email al admin ---
            unlock_link = f"http://{db_host}:{front_port}/admin/users" 
            send_unlock_email(user_info, unlock_link)
            
        else:
            sql_update = "UPDATE users SET failed_attempts = %s WHERE id = %s"
            cursor.execute(sql_update, (new_attempts, user_id))
        
        db_connection.commit()
    except Exception as e:
        db_connection.rollback()
        print(f"Error al aumentar intentos fallidos: {e}")
    finally:
        cursor.close()















# # Resetea el contador de intentos fallidos a 0 y desbloquea la cuenta.
# def reset_failed_attempts(db_connection: mysql.connector.MySQLConnection, user_id: int):
   
#     cursor = db_connection.cursor()
#     try:
#         sql_update = "UPDATE users SET failed_attempts = 0, is_locked = FALSE WHERE id = %s"
#         cursor.execute(sql_update, (user_id,))
#         db_connection.commit() # Guarda los cambios
#     except Exception as e:
#         db_connection.rollback() # Revertir si hay un error
#         print(f"Error al resetear intentos fallidos: {e}")
#     finally:
#         cursor.close()
