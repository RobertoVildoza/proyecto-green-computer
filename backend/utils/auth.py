from datetime import UTC, datetime, timedelta
from jose import JWTError, jwt # type: ignore
from passlib.context import CryptContext # type: ignore
from fastapi import Depends, HTTPException # type: ignore
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # type: ignore
import os
import random
import string
from dotenv import load_dotenv # type: ignore

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET", "changeme")
ALGORITHM  = os.getenv("JWT_ALGORITHM", "HS256")
EXPIRE_MIN = int(os.getenv("JWT_EXPIRE_MINUTES", 480))

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer  = HTTPBearer()

def hash_password(plain: str) -> str:
    return pwd_ctx.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)

def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(UTC) + timedelta(minutes=EXPIRE_MIN)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    from database import query
    payload = decode_token(creds.credentials)
    id_usuario = payload.get("sub")
    if id_usuario is None:
        raise HTTPException(status_code=401, detail="Token inválido.")
    
    rows = query(
        """
        SELECT u.id_usuario, u.username, u.activo,
               c.id_cliente, c.nombre, c.apellido, c.email, c.empresa, c.telefono
        FROM usuario_portal u
        JOIN cliente c ON c.id_cliente = u.id_cliente
        WHERE u.id_usuario = :id_usuario AND u.activo = 1
        """,
        {"id_usuario": int(id_usuario)}
    )
    if not rows:
        raise HTTPException(status_code=401, detail="Usuario no encontrado o inactivo.")
    return rows[0]

reset_codes: dict = {}

def generate_reset_code(email: str) -> str:
    code = ''.join(random.choices(string.digits, k=6))
    reset_codes[email] = code
    print(f"[RESET CODE] Email: {email}  Código: {code}")
    return code


def clear_reset_code(email: str):
    reset_codes.pop(email, None)
 