from fastapi import Depends, HTTPException
from app.schemas.users.UsersSchema import UserCreate, UserLogin
from app.utils.dbConn import get_db_connection
from app.utils.security import create_access_token
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.utils.security import SECRET_KEY, ALGORITHM
import mysql.connector

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


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


 # Aumenta el contador de intentos fallidos para un usuario.
# Si excede un limite bloquea la cuenta.
def increase_failed_attempts(db_connection: mysql.connector.MySQLConnection, user_id: int):
    
    cursor = db_connection.cursor()
    try:
        # Obtener el número actual de intentos fallidos
        cursor.execute("SELECT failed_attempts FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        current_attempts = result[0] if result else 0

        new_attempts = current_attempts + 1
        
        #  bloquear la cuenta si se supera el límite
        if new_attempts >= 5: # Se puede ajustar aqui el limite
            sql_update = "UPDATE users SET failed_attempts = %s, is_locked = TRUE WHERE id = %s"
            cursor.execute(sql_update, (new_attempts, user_id))
        else:
            sql_update = "UPDATE users SET failed_attempts = %s WHERE id = %s"
            cursor.execute(sql_update, (new_attempts, user_id))
        
        db_connection.commit() # Guarda los cambios
    except Exception as e:
        db_connection.rollback() # Revertir si hay un error
        print(f"Error al aumentar intentos fallidos: {e}")
    finally:
        cursor.close()



# Resetea el contador de intentos fallidos a 0 y desbloquea la cuenta.
def reset_failed_attempts(db_connection: mysql.connector.MySQLConnection, user_id: int):
   
    cursor = db_connection.cursor()
    try:
        sql_update = "UPDATE users SET failed_attempts = 0, is_locked = FALSE WHERE id = %s"
        cursor.execute(sql_update, (user_id,))
        db_connection.commit() # Guarda los cambios
    except Exception as e:
        db_connection.rollback() # Revertir si hay un error
        print(f"Error al resetear intentos fallidos: {e}")
    finally:
        cursor.close()
