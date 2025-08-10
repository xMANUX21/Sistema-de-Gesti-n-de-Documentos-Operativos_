import os
from dotenv import load_dotenv
from sqlmodel import Field,Session,create_engine,select,SQLModel
from typing import Annotated

from fastapi import FastAPI, Depends

load_dotenv()

db_username= os.getenv('USER_DB')
db_password= os.getenv('PASSWORD_DB')
db_host=os.getenv('HOST_DB')
db_name=os.getenv('NAME_DB')


#Esto va a ir en el .env
url_connection = f'mysql+pymysql://{db_username}:{db_password}@{db_host}:3306/{db_name}'

engine=create_engine(url_connection)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session # Se trabaja con una conexion por sesion , para no tener que cada vez crear una nueva

session_dep=Annotated[Session,Depends(get_session)] # Hace que cada vez que se llame a session dep , se haga una nueva sesion 
