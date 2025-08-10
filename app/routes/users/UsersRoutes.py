from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session,select
from app.utils.dbConn import get_db_connection
from app.utils.security import get_current_user
import mysql.connector
from app.utils.dependencies import is_admin
from app.schemas.users.UsersSchema import UserResponse 

router = APIRouter(tags=["users"])


#El login y register estan en auth Routes

@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user


#Optener usuarios solo admin
@router.get("/")
def get_all_users(
    db_connection: mysql.connector.MySQLConnection = Depends(get_db_connection),
    # Llama a la dependencia de validación de rol aquí
    is_admin_user: bool = Depends(is_admin) 
):
    # Si pasamos de este punto, significa que el usuario ya fue validado como admin
    cursor = db_connection.cursor(dictionary=True)
    sql_query = "SELECT id, name, email, role FROM users"
    cursor.execute(sql_query)
    users_data = cursor.fetchall()
    cursor.close()
    
    return {"users": users_data}

#Borrar un usuario solo admin
# @router.delete("/{id}", status_code=204)
# def delete_user(id: int, session: Session = Depends(db_conn_dep), current_user: User = Depends(get_current_user)):
#     if current_user.role != "admin":
#         raise HTTPException(status_code=403, detail="Solo los administradores pueden eliminar usuarios")
#     user = session.get(User, id)
#     if not user:
#         raise HTTPException(status_code=404, detail="Usuario no encontrado")
#     session.delete(user)
#     session.commit()
