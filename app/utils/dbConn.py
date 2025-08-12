import os
import mysql.connector
from dotenv import load_dotenv
from fastapi import Depends
from typing import Generator
from mysql.connector import Error
load_dotenv()

db_username = os.getenv('USER_DB')
db_password = os.getenv('PASSWORD_DB')
db_host = os.getenv('HOST_DB')
db_name = os.getenv('NAME_DB')

DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com") #Se le ponen otro argumentos si en algun caso no se habian definido
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")

#Con esta funcion verificamos si hay una base de datos ya creada si no es asi la hara con el nombre de dbname que tengamos en nuestro .env 
def init_database():
    try:
        # Conexion sin DB
        conn_temp = mysql.connector.connect( #Nos conectamos al sevidor de MYSQL
            host=db_host,
            user=db_username,
            password=db_password
        )
        cursor_temp = conn_temp.cursor()#Cursor en donde vamos a darle instrucciones ya en el servidor conectado
        cursor_temp.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}") #Se ejecuta este comando
        conn_temp.commit()#Guardamos el cambio
        cursor_temp.close()
        conn_temp.close() #Cerramos el servidor y cursor temporal 
        print(f" Base de datos '{db_name}' verificada/creada.")
    except Error as e:
        print(f" Error creando/verificando base de datos: {e}")

#  Dependencia para obtener conexión a MySQL
def get_db_connection() -> Generator[mysql.connector.MySQLConnection, None, None]:
    connection = mysql.connector.connect(
        host=db_host,
        user=db_username,
        password=db_password,
        database=db_name
    )
    try:
        yield connection
    finally:
        if connection.is_connected():
            connection.close()


#  Función para inicializar la DB y tablas
def create_db_and_tables():
    try:
        startup_db_connection = mysql.connector.connect(
            host=db_host,
            user=db_username,
            password=db_password,
            database=db_name
        )
        cursor = startup_db_connection.cursor()

        # === Tabla de usuarios (tema operadores) ===
        create_users_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(50) DEFAULT 'operador',
            department VARCHAR(255),
            failed_attempts INT DEFAULT 0,
            is_locked BOOLEAN DEFAULT FALSE
        );
        """
        cursor.execute(create_users_sql)

        # === Tabla de documentos PDF ===
        create_documents_sql = """
        CREATE TABLE IF NOT EXISTS documentos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            contenido LONGTEXT NOT NULL,
            fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_documents_sql)
        #Proceso para que se cree el primer usuario que sera admin
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        if total_users == 0:
            from .security import hash_password #Lo importamos aqui para que no hayan comflictos ya que importan ambos
            hashed_password = hash_password(DEFAULT_ADMIN_PASSWORD)
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, role)
                VALUES (%s, %s, %s, %s)
                 """, ("Administrador", DEFAULT_ADMIN_EMAIL, hashed_password, "admin"))
            print(f" Se creo el usuario admin ==> email='{DEFAULT_ADMIN_EMAIL}', password='{DEFAULT_ADMIN_PASSWORD}'")


        startup_db_connection.commit()
        print("Tablas 'users' y 'documentos' verificadas/creadas exitosamente.")
        cursor.close()

    except mysql.connector.Error as err:
        print(f"Error al crear o verificar tablas: {err}")

    finally:
        if 'startup_db_connection' in locals() and startup_db_connection.is_connected():
            startup_db_connection.close()
