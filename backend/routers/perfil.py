from fastapi import APIRouter, Depends, HTTPException # type: ignore
from pydantic import BaseModel # type: ignore
from typing import Optional
from database import query, execute
from utils.auth import get_current_user, verify_password, hash_password

router = APIRouter(prefix="/perfil", tags=["Perfil"])

class PerfilUpdate(BaseModel):
    nombre:   Optional[str] = None
    apellido: Optional[str] = None   
    email:    Optional[str] = None
    empresa:  Optional[str] = None 
    telefono: Optional[str] = None  


class ChangePassInput(BaseModel):
    current_password: str
    new_password: str

@router.get("/")
def get_perfil(user: dict = Depends(get_current_user)):
    """
    Cambios:
    - tabla usuarios      → JOIN entre usuario_portal y cliente
    - campo id            → id_usuario (alias AS id para no romper el JS)
    - campo nombre        → devuelve nombre + apellido por separado
    - campo created_at    → u.created_at (viene de usuario_portal)
    - campos nuevos       → apellido, empresa, telefono
    """
    row = query(
        """
        SELECT
            u.id_usuario                            AS id,
            u.username,
            c.email,
            c.nombre,
            c.apellido,
            c.empresa,
            c.telefono,
            u.created_at
        FROM usuario_portal u
        JOIN cliente c ON c.id_cliente = u.id_cliente
        WHERE u.id_usuario = :id_usuario
        LIMIT 1
        """,
        {"id_usuario": user["id_usuario"]},
        fetchone=True
    )
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return row

@router.put("/")
def actualizar_perfil(body: PerfilUpdate, user: dict = Depends(get_current_user)):
    """
    Los datos del perfil ahora viven en la tabla 'cliente'.
    El username sigue en usuario_portal pero no es editable desde acá.
    """
    if not any([body.nombre, body.apellido, body.email, body.empresa, body.telefono]):
        raise HTTPException(status_code=400, detail="Enviá al menos un campo para actualizar.")

    if body.nombre and len(body.nombre.strip()) < 2:
        raise HTTPException(status_code=400, detail="El nombre es muy corto.")

    if body.email:
        existing = query(
            """
            SELECT c.id_cliente FROM cliente c
            JOIN usuario_portal u ON u.id_cliente = c.id_cliente
            WHERE c.email = :email AND u.id_usuario != :id_usuario
            LIMIT 1
            """,
            {"email": body.email, "id_usuario": user["id_usuario"]},
            fetchone=True
        )
        if existing:
            raise HTTPException(status_code=400, detail="Ese email ya está en uso por otro usuario.")

    execute(
        """
        UPDATE cliente c
        JOIN usuario_portal u ON u.id_cliente = c.id_cliente
        SET
            c.nombre   = COALESCE(:nombre,   c.nombre),
            c.apellido = COALESCE(:apellido, c.apellido),
            c.email    = COALESCE(:email,    c.email),
            c.empresa  = COALESCE(:empresa,  c.empresa),
            c.telefono = COALESCE(:telefono, c.telefono)
        WHERE u.id_usuario = :id_usuario
        """,
        {
            "nombre":     body.nombre.strip()   if body.nombre   else None,
            "apellido":   body.apellido.strip() if body.apellido else None,
            "email":      body.email.strip()    if body.email    else None,
            "empresa":    body.empresa.strip()  if body.empresa  else None,
            "telefono":   body.telefono.strip() if body.telefono else None,
            "id_usuario": user["id_usuario"],
        }
    )
    return {"message": "Perfil actualizado correctamente."}

@router.put("/cambiar-password")
def cambiar_password(body: ChangePassInput, user: dict = Depends(get_current_user)):
    """
    Cambios:
    - tabla usuarios      → usuario_portal
    - campo password_hash → contrasenia
    - campo id            → id_usuario
    """
    row = query(
        "SELECT contrasenia FROM usuario_portal WHERE id_usuario = :id_usuario LIMIT 1",
        {"id_usuario": user["id_usuario"]},
        fetchone=True
    )
    if not row or not verify_password(body.current_password, row["contrasenia"]):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta.")

    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="Mínimo 8 caracteres.")

    execute(
        "UPDATE usuario_portal SET contrasenia = :hash WHERE id_usuario = :id_usuario",
        {"hash": hash_password(body.new_password), "id_usuario": user["id_usuario"]}
    )
    return {"message": "Contraseña actualizada correctamente."}


@router.delete("/")
def desactivar_cuenta(user: dict = Depends(get_current_user)):
    """
    Cambios:
    - tabla usuarios  → usuario_portal
    - campo id        → id_usuario
    """
    execute(
        "UPDATE usuario_portal SET activo = 0 WHERE id_usuario = :id_usuario",
        {"id_usuario": user["id_usuario"]}
    )
    return {"message": "Cuenta desactivada. Contactá a soporte para reactivarla."}
