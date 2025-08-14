import os
import mysql.connector
from dotenv import load_dotenv
from fastapi import Depends
from typing import Generator

load_dotenv()

db_username = os.getenv('USER_DB')
db_password = os.getenv('PASSWORD_DB')
db_host = os.getenv('HOST_DB')
db_name = os.getenv('NAME_DB')


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

        # === Tabla de metadatos de tablas extraídas ===
        create_tables_meta_sql = """
        CREATE TABLE IF NOT EXISTS document_tables (
            id INT AUTO_INCREMENT PRIMARY KEY,
            document_id INT NOT NULL,
            table_uid VARCHAR(50) NOT NULL,
            page INT NOT NULL,
            bbox TEXT,
            n_rows INT,
            n_cols INT,
            detection VARCHAR(20),
            confidence FLOAT,
            title_guess TEXT,
            headers JSON,
            rows_data JSON,
            FOREIGN KEY (document_id) REFERENCES documentos(id) ON DELETE CASCADE
        );
        """
        cursor.execute(create_tables_meta_sql)

        startup_db_connection.commit()
        print("Tablas 'users', 'documentos' y 'document_tables' verificadas/creadas exitosamente.")
        cursor.close()

    except mysql.connector.Error as err:
        print(f"Error al crear o verificar tablas: {err}")

    finally:
        if 'startup_db_connection' in locals() and startup_db_connection.is_connected():
            startup_db_connection.close()
