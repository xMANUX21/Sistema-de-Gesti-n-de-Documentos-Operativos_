from app.utils.dbConn import init_database,create_db_and_tables
from fastapi import FastAPI, Depends
# from app.auth.controller import router as auth_router
from app.routes.auth_routes import router as loginRouter
from app.routes.users.UsersRoutes import router as userRouter
from app.routes.documents.DocumentRoutes import router as documentRouter
from app.routes.users.AdminRoutes import router as adminRouter
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()

# Configuración de CORS
origins = [
    "http://localhost:3000",  # El origen del frontend
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(auth_router, prefix="/api/auth")
app.include_router(loginRouter, prefix="/api/auth")
app.include_router(userRouter,prefix="/api/users")
app.include_router(documentRouter, prefix="/api")
app.include_router(adminRouter, prefix="/api/admin")



@app.get("/")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)


@app.on_event('startup')
async def on_startup():
    print("Inicio de startup async")
    await asyncio.to_thread(init_database)
    print("init_database() terminó")
    await asyncio.to_thread(create_db_and_tables)
    print("create_db_and_tables() terminó")
