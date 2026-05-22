import httpx # type: ignore
import os
from dotenv import load_dotenv # type: ignore

load_dotenv()

AUTH0_DOMAIN       = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID    = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_AUDIENCE     = os.getenv("AUTH0_AUDIENCE")


def get_auth0_token() -> str:
    """Obtiene un token de acceso para la Management API de Auth0."""
    response = httpx.post(
        f"https://{AUTH0_DOMAIN}/oauth/token",
        json={
            "client_id":     AUTH0_CLIENT_ID,
            "client_secret": AUTH0_CLIENT_SECRET,
            "audience":      AUTH0_AUDIENCE,
            "grant_type":    "client_credentials"
        }
    )
    response.raise_for_status()
    return response.json()["access_token"]

def get_auth0_token() -> str:
    print(f"[AUTH0 DEBUG] DOMAIN: {AUTH0_DOMAIN}")
    print(f"[AUTH0 DEBUG] CLIENT_ID: {AUTH0_CLIENT_ID}")
    print(f"[AUTH0 DEBUG] AUDIENCE: {AUTH0_AUDIENCE}")
    print(f"[AUTH0 DEBUG] SECRET (primeros 5 chars): {AUTH0_CLIENT_SECRET[:5] if AUTH0_CLIENT_SECRET else 'None'}")

    response = httpx.post(
        f"https://{AUTH0_DOMAIN}/oauth/token",
        json={
            "client_id":     AUTH0_CLIENT_ID,
            "client_secret": AUTH0_CLIENT_SECRET,
            "audience":      AUTH0_AUDIENCE,
            "grant_type":    "client_credentials"
        }
    )
    response.raise_for_status()
    return response.json()["access_token"]


def sync_user_auth0(email: str, username: str, nombre: str) -> dict:
    """
    Sincroniza el usuario con Auth0 al hacer login.
    Si no existe lo crea, si ya existe lo actualiza.
    """
    token = get_auth0_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Buscar si el usuario ya existe en Auth0
    search = httpx.get(
        f"https://{AUTH0_DOMAIN}/api/v2/users-by-email",
        headers=headers,
        params={"email": email}
    )
    search.raise_for_status()
    usuarios = search.json()

    if usuarios:
        # Ya existe → actualizar nombre
        user_id = usuarios[0]["user_id"]
        httpx.patch(
            f"https://{AUTH0_DOMAIN}/api/v2/users/{user_id}",
            headers=headers,
            json={"name": nombre, "nickname": username}
        )
        return {"accion": "actualizado", "auth0_id": user_id}
    else:
        # No existe → crear
        create = httpx.post(
            f"https://{AUTH0_DOMAIN}/api/v2/users",
            headers=headers,
            json={
                "email":      email,
                "name":       nombre,
                "nickname":   username,
                "connection": "Username-Password-Authentication",
                "password":   "Auth0Sync#2026!",
                "email_verified": True
            }
        )
        create.raise_for_status()
        return {"accion": "creado", "auth0_id": create.json()["user_id"]}
    
    
    