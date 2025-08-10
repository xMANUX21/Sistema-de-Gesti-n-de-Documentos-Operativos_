from .utils.dbConn import create_db_and_tables
from fastapi import FastAPI, Depends
# from app.auth.controller import router as auth_router
from app.routes.auth_routes import router as loginRouter
from app.routes.users.UsersRoutes import router as userRouter


app = FastAPI()

# app.include_router(auth_router, prefix="/api/auth")
app.include_router(loginRouter, prefix="/api/auth")
app.include_router(userRouter,prefix="/api/users")


@app.get("/")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)


@app.on_event('startup')
def on_startup():
    create_db_and_tables() # Verifica cada vez que corramos nuestro programa que se tengan las tablas y la base de datos
