from app.utils.dbConn import create_db_and_tables ,init_database
from fastapi import FastAPI, Depends
# from app.auth.controller import router as auth_router
from app.routes.auth_routes import router as loginRouter
from app.routes.users.UsersRoutes import router as userRouter
from app.routes.documents.document_routes import router as documentRouter
from app.routes.users.AdminRoutes import router as adminRouter

app = FastAPI()

# app.include_router(auth_router, prefix="/api/auth")
app.include_router(loginRouter, prefix="/api/auth")
app.include_router(userRouter,prefix="/api/users")
app.include_router(documentRouter, prefix="/api/documents")
app.include_router(adminRouter, prefix="/api/admin")



@app.get("/")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)


@app.on_event('startup')
def on_startup():
    init_database() # Para que verifique si existe la base de datos o no
    create_db_and_tables() # Verifica cada vez que corramos nuestro programa que se tengan las tablas y la base de datos
