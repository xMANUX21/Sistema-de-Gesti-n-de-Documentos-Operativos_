from fastapi import APIRouter, Depends, HTTPException, status
from app.utils.dependencies import is_admin
from app.utils.dbConn import get_db_connection
import mysql.connector

router = APIRouter(tags=["admin"])

# Desbloquea una cuenta de usuario y resetea los intentos fallidos.
 # Solo accesible para administradores.
@router.put("/users/{user_id}/unlock")
def unlock_user_account(
    user_id: int,
    db_connection: mysql.connector.MySQLConnection = Depends(get_db_connection),
    is_admin_user: bool = Depends(is_admin) # Protege el endpoint
):
    cursor = db_connection.cursor()
    try:
        sql_update = "UPDATE users SET is_locked = FALSE, failed_attempts = 0 WHERE id = %s" # Accede al id que se le ingrese , para cambiar el campo de true a false , de 1 a 0
        cursor.execute(sql_update, (user_id,))
        
        # Si no se encontro , manda el manejo de errores
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        
        db_connection.commit()
        return {"message": f"Cuenta del usuario {user_id} desbloqueada."}
    except Exception as e:
        db_connection.rollback()
        raise e
    finally:
        cursor.close()



#Listado de los usuarios que estan bloqueados
@router.get("/locked-users")
def get_locked_users(
    db_connection: mysql.connector.MySQLConnection = Depends(get_db_connection),
    is_admin_user: bool = Depends(is_admin) # Protege el endpoint
):
    #Retorna la lista de usuarios con la cuenta bloqueada.
    
    cursor = db_connection.cursor(dictionary=True)
    try:
        sql_select = "SELECT id, name, email FROM users WHERE is_locked = TRUE" #Busca los que tengan locked =true
        cursor.execute(sql_select)
        locked_users = cursor.fetchall() # Con esto nos trae a todos
        return locked_users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del servidor: {e}")
    finally:
        cursor.close()