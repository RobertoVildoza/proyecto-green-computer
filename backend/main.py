from fastapi import FastAPI, Depends, HTTPException # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from pydantic import BaseModel # type: ignore
from dotenv import load_dotenv # type: ignore
import os

load_dotenv()

from routers.auth      import router as auth_router
from routers.contratos import router as contratos_router
from routers.tickets   import router as tickets_router
from routers.equipos   import router as equipos_router
from routers.carbono   import router as carbono_router
from routers.perfil    import router as perfil_router
from utils.auth        import get_current_user, verify_password, hash_password
from database          import query, execute

app = FastAPI(
    title="Green Computer API",
    description="API del Portal del Cliente Green Computer - Alquiler de Tecnología Sustentable",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(contratos_router)
app.include_router(tickets_router)
app.include_router(equipos_router)
app.include_router(carbono_router)
app.include_router(perfil_router)


class ChangePassInput(BaseModel):
    current_password: str
    new_password: str


@app.post("/auth/change-password", tags=["Auth"])
def change_password(body: ChangePassInput, user: dict = Depends(get_current_user)):
    """
    Cambios respecto a la versión anterior:
    - tabla usuarios      → usuario_portal
    - campo password_hash → contrasenia
    - campo id            → id_usuario
    """
    db_user = query(
        "SELECT contrasenia FROM usuario_portal WHERE id_usuario = :id_usuario LIMIT 1",
        {"id_usuario": user["id_usuario"]},
        fetchone=True
    )
    if not db_user or not verify_password(body.current_password, db_user["contrasenia"]):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta.")
    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="La nueva contraseña debe tener al menos 8 caracteres.")

    execute(
        "UPDATE usuario_portal SET contrasenia = :hash WHERE id_usuario = :id_usuario",
        {"hash": hash_password(body.new_password), "id_usuario": user["id_usuario"]}
    )
    return {"message": "Contraseña actualizada correctamente."}


@app.get("/", tags=["Root"])
def root():
    return {"status": "ok", "app": "Green Computer API v2.0", "docs": "/docs"}


@app.get("/health", tags=["Root"])
def health():
    try:
        from database import get_connection
        conn = get_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
    