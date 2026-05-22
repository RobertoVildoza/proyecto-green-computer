from fastapi import APIRouter, HTTPException # type: ignore
from pydantic import BaseModel # type: ignore
from typing import Optional
from database import query, execute
from utils.auth import (
    verify_password, hash_password, create_token,
    generate_reset_code, clear_reset_code, reset_codes
)
from utils.auth0 import sync_user_auth0

router = APIRouter(prefix="/auth", tags=["Auth"])

class LoginInput(BaseModel):
    username: str
    password: str

class RegisterInput(BaseModel):
    nombre:    str
    apellido:  str
    email:     str
    telefono:  Optional[str] = None
    empresa:   Optional[str] = None
    username:  str
    password:  str

class ForgotInput(BaseModel):
    email: str

class ResetInput(BaseModel):
    code: str
    new_password: str

@router.post("/login")
def login(body: LoginInput):
    user = query(
        """
        SELECT
            u.id_usuario,
            u.username,
            u.contrasenia,
            c.id_cliente,
            c.nombre,
            c.apellido,
            c.email
        FROM usuario_portal u
        JOIN cliente c ON c.id_cliente = u.id_cliente
        WHERE (u.username = :usr OR c.email = :usr)
          AND u.activo = 1
        LIMIT 1
        """,
        {"usr": body.username},
        fetchone=True
    )

    if not user or not verify_password(body.password, user["contrasenia"]):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos.")

    token = create_token({
        "sub":      str(user["id_usuario"]),
        "nombre":   user["nombre"],
        "email":    user["email"],
        "username": user["username"]
    })

    # ── Sincronización con Auth0 ──────────────────────────────────────
    # No bloquea el login si Auth0 falla
    try:
        auth0_result = sync_user_auth0(
            email=user["email"],
            username=user["username"],
            nombre=f"{user['nombre']} {user['apellido']}"
        )
        print(f"[AUTH0] Usuario sincronizado: {auth0_result}")
    except Exception as e:
        print(f"[AUTH0] Error al sincronizar (login no afectado): {e}")
    # ─────────────────────────────────────────────────────────────────

    return {
        "access_token": token,
        "token_type":   "bearer",
        "user": {
            "id":       user["id_usuario"],
            "nombre":   f"{user['nombre']} {user['apellido']}",
            "email":    user["email"],
            "username": user["username"]
        }
    }

@router.post("/register")
def register(body: RegisterInput):
    if len(body.nombre.strip()) < 2:
        raise HTTPException(status_code=400, detail="El nombre es demasiado corto.")
    if len(body.apellido.strip()) < 2:
        raise HTTPException(status_code=400, detail="El apellido es demasiado corto.")
    if "@" not in body.email or "." not in body.email:
        raise HTTPException(status_code=400, detail="El email no es válido.")
    if len(body.username.strip()) < 3:
        raise HTTPException(status_code=400, detail="El usuario debe tener al menos 3 caracteres.")
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres.")

    existing_user = query(
        "SELECT id_usuario FROM usuario_portal WHERE username = :username LIMIT 1",
        {"username": body.username.strip()},
        fetchone=True
    )
    if existing_user:
        raise HTTPException(status_code=409, detail="El nombre de usuario ya está en uso.")

    existing_email = query(
        "SELECT id_cliente FROM cliente WHERE email = :email LIMIT 1",
        {"email": body.email.strip().lower()},
        fetchone=True
    )
    if existing_email:
        raise HTTPException(status_code=409, detail="Ya existe una cuenta con ese email.")

    id_cliente = execute(
        """
        INSERT INTO cliente (nombre, apellido, email, telefono, empresa)
        VALUES (:nombre, :apellido, :email, :telefono, :empresa)
        """,
        {
            "nombre":   body.nombre.strip(),
            "apellido": body.apellido.strip(),
            "email":    body.email.strip().lower(),
            "telefono": body.telefono.strip() if body.telefono else None,
            "empresa":  body.empresa.strip() if body.empresa else None,
        }
    )

    hashed = hash_password(body.password)
    execute(
        """
        INSERT INTO usuario_portal (id_cliente, username, contrasenia, activo)
        VALUES (:id_cliente, :username, :contrasenia, 1)
        """,
        {
            "id_cliente":  id_cliente,
            "username":    body.username.strip(),
            "contrasenia": hashed,
        }
    )

    return {
        "message": "Cuenta creada correctamente. Ya podés iniciar sesión.",
        "username": body.username.strip()
    }

@router.post("/forgot-password")
def forgot_password(body: ForgotInput):
    user = query(
        """
        SELECT u.id_usuario, c.email
        FROM usuario_portal u
        JOIN cliente c ON c.id_cliente = u.id_cliente
        WHERE c.email = :email
          AND u.activo = 1
        LIMIT 1
        """,
        {"email": body.email},
        fetchone=True
    )

    if not user:
        raise HTTPException(status_code=404, detail="No existe una cuenta con ese email.")

    generate_reset_code(body.email)
    return {"message": "Código enviado al email registrado."}

@router.post("/reset-password")
def reset_password(body: ResetInput):
    email = next((e for e, c in reset_codes.items() if c == body.code), None)
    if not email:
        raise HTTPException(status_code=400, detail="Código inválido o expirado.")

    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres.")

    new_hash = hash_password(body.new_password)

    execute(
        """
        UPDATE usuario_portal u
        JOIN cliente c ON c.id_cliente = u.id_cliente
        SET u.contrasenia = :hash
        WHERE c.email = :email
        """,
        {"hash": new_hash, "email": email}
    )

    clear_reset_code(email)
    return {"message": "Contraseña actualizada correctamente."}

class GoogleLoginInput(BaseModel):
    email: str
    name:  str

@router.post("/login-google")
def login_google(body: GoogleLoginInput):
    # Buscar usuario por email en la BD
    user = query(
        """
        SELECT
            u.id_usuario,
            u.username,
            c.id_cliente,
            c.nombre,
            c.apellido,
            c.email
        FROM usuario_portal u
        JOIN cliente c ON c.id_cliente = u.id_cliente
        WHERE c.email = :email
          AND u.activo = 1
        LIMIT 1
        """,
        {"email": body.email},
        fetchone=True
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="No existe una cuenta registrada con ese email de Google. Registrate primero."
        )

    token = create_token({
        "sub":      str(user["id_usuario"]),
        "nombre":   user["nombre"],
        "email":    user["email"],
        "username": user["username"]
    })

    # Sincronizar con Auth0
    try:
        sync_user_auth0(
            email=user["email"],
            username=user["username"],
            nombre=f"{user['nombre']} {user['apellido']}"
        )
    except Exception as e:
        print(f"[AUTH0 SYNC] Error: {e}")

    return {
        "access_token": token,
        "token_type":   "bearer",
        "user": {
            "id":       user["id_usuario"],
            "nombre":   f"{user['nombre']} {user['apellido']}",
            "email":    user["email"],
            "username": user["username"]
        }
    }
