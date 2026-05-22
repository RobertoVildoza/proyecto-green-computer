import mysql.connector # type: ignore
from mysql.connector import Error # type: ignore
import os
import re
from dotenv import load_dotenv # type: ignore

load_dotenv()

def get_connection():
    """Retorna una conexión a MySQL."""
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            database=os.getenv("DB_NAME", "portal_clientes"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "root"),
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci",
        )
        return conn
    except Error as e:
        print(f"[DB ERROR] {e}")
        raise e

def _convert_params(sql: str, params):
    """
    Convierte named parameters estilo :nombre a %s para mysql.connector.

    Ejemplos:
        "WHERE id = :id"            + {"id": 5}
        "WHERE id = :id AND x = :x" + {"id": 5, "x": 3}

    mysql.connector no soporta :nombre nativamente, solo %s o %(nombre)s.
    Esta función reemplaza :nombre por %s y reordena los valores
    en el mismo orden en que aparecen en el SQL.
    """
    if params is None:
        return sql, ()

    if isinstance(params, (tuple, list)):
        return sql, params

    keys_in_order = re.findall(r":([a-zA-Z_][a-zA-Z0-9_]*)", sql)

    converted_sql = re.sub(r":[a-zA-Z_][a-zA-Z0-9_]*", "%s", sql)

    values = tuple(params[k] for k in keys_in_order)

    return converted_sql, values


def query(sql: str, params=None, fetchone=False):
    """Ejecuta una SELECT y retorna resultados como lista de dicts.
    Soporta tanto :nombre como %s como placeholders.
    """
    converted_sql, converted_params = _convert_params(sql, params)
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute(converted_sql, converted_params or ())
    result = cur.fetchone() if fetchone else cur.fetchall()
    cur.close()
    conn.close()
    return result


def execute(sql: str, params=None):
    """Ejecuta INSERT/UPDATE/DELETE. Retorna lastrowid.
    Soporta tanto :nombre como %s como placeholders.
    """
    converted_sql, converted_params = _convert_params(sql, params)
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(converted_sql, converted_params or ())
    conn.commit()
    lid = cur.lastrowid
    cur.close()
    conn.close()
    return lid
