from fastapi import APIRouter, Depends, HTTPException # type: ignore
from database import query
from utils.auth import get_current_user

router = APIRouter(prefix="/contratos", tags=["Contratos"])

@router.get("/mis-contratos")
def mis_contratos(user: dict = Depends(get_current_user)):
    """
    Devuelve todos los contratos del usuario autenticado.
    Cambios respecto a la versión anterior:
    - tabla contratos       → contrato_alquiler
    - tabla equipos         → equipo  (con detalle_contrato como intermedia)
    - campo usuario_id      → id_cliente
    - campo e.nombre        → e.nombre_equipo AS equipo_nombre  (alias para no romper el JS)
    - campo c.fecha_fin     → c.fecha_vencim  AS fecha_fin      (alias para no romper el JS)
    - campos nuevos         → tipo_contrato, cuotas_total, cuotas_pagadas
    """
    rows = query(
        """
        SELECT
            ca.id_contrato                          AS id,
            ca.fecha_inicio,
            ca.fecha_vencim                         AS fecha_fin,
            ca.valor_mensual,
            ca.tipo_contrato,
            ca.cuotas_total,
            ca.cuotas_pagadas,
            ca.estado,
            ca.notas,
            GROUP_CONCAT(e.nombre_equipo SEPARATOR ', ') AS equipo_nombre,
            GROUP_CONCAT(e.modelo        SEPARATOR ', ') AS equipo_modelo
        FROM contrato_alquiler ca
        LEFT JOIN detalle_contrato dc ON dc.id_contrato = ca.id_contrato
        LEFT JOIN equipo e            ON e.id_equipo    = dc.id_equipo
        WHERE ca.id_cliente = :id_cliente
        GROUP BY ca.id_contrato
        ORDER BY ca.fecha_inicio DESC
        """,
        {"id_cliente": user["id_cliente"]}
    )
    return rows

@router.get("/{id_contrato}")
def detalle_contrato(id_contrato: int, user: dict = Depends(get_current_user)):
    """
    Devuelve el detalle completo de un contrato individual.
    Incluye todos los equipos asociados al contrato.
    """
    rows = query(
        """
        SELECT
            ca.id_contrato                  AS id,
            ca.fecha_inicio,
            ca.fecha_vencim                 AS fecha_fin,
            ca.valor_mensual,
            ca.tipo_contrato,
            ca.cuotas_total,
            ca.cuotas_pagadas,
            ca.estado,
            ca.notas,
            e.id_equipo,
            e.nombre_equipo                 AS equipo_nombre,
            e.modelo                        AS equipo_modelo,
            e.fabricante,
            e.specs,
            e.numero_serie
        FROM contrato_alquiler ca
        JOIN detalle_contrato dc ON dc.id_contrato = ca.id_contrato
        JOIN equipo e            ON e.id_equipo    = dc.id_equipo
        WHERE ca.id_contrato = :id_contrato
          AND ca.id_cliente  = :id_cliente
        """,
        {"id_contrato": id_contrato, "id_cliente": user["id_cliente"]}
    )

    if not rows:
        raise HTTPException(status_code=404, detail="Contrato no encontrado.")

    return rows
