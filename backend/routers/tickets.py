from fastapi import APIRouter, Depends, HTTPException # type: ignore
from pydantic import BaseModel # type: ignore
from typing import Optional
from database import query, execute
from utils.auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/tickets", tags=["Tickets"])

class TicketInput(BaseModel):
    tipo: str
    equipo_id: Optional[int] = None 
    asunto: str
    detalle: str                    

class TicketUpdate(BaseModel):
    asunto: str
    detalle: str

@router.post("/crear")
def crear_ticket(body: TicketInput, user: dict = Depends(get_current_user)):
    if body.tipo not in ("consulta", "garantia"):
        raise HTTPException(status_code=400, detail="Tipo inválido.")
    if len(body.asunto.strip()) < 3:
        raise HTTPException(status_code=400, detail="El asunto es muy corto.")

    new_id = execute(
        """
        INSERT INTO ticket_soporte
            (id_cliente, id_equipo, tipo, asunto, descripcion, estado, fecha_ticket)
        VALUES
            (:id_cliente, :id_equipo, :tipo, :asunto, :descripcion, 'abierto', :fecha)
        """,
        {
            "id_cliente":  user["id_cliente"],   
            "id_equipo":   body.equipo_id,       
            "tipo":        body.tipo,
            "asunto":      body.asunto.strip(),
            "descripcion": body.detalle,         
            "fecha":       datetime.now(),
        }
    )
    return {"id": new_id, "message": "Ticket creado correctamente."}

@router.get("/mis-tickets")
def mis_tickets(user: dict = Depends(get_current_user)):
    rows = query(
        """
        SELECT
            t.id_ticket                     AS id,
            t.tipo,
            t.asunto,
            t.descripcion                   AS detalle,
            t.estado,
            t.fecha_ticket                  AS fecha_ticket,
            t.id_equipo                     AS equipo_id,
            e.nombre_equipo                 AS equipo_nombre
        FROM ticket_soporte t
        LEFT JOIN equipo e ON e.id_equipo = t.id_equipo
        WHERE t.id_cliente = :id_cliente
        ORDER BY t.fecha_ticket DESC
        """,
        {"id_cliente": user["id_cliente"]}
    )
    return rows

@router.put("/{ticket_id}")
def actualizar_ticket(ticket_id: int, body: TicketUpdate, user: dict = Depends(get_current_user)):
    ticket = query(
        """
        SELECT id_ticket AS id, estado
        FROM ticket_soporte
        WHERE id_ticket = :id AND id_cliente = :id_cliente
        LIMIT 1
        """,
        {"id": ticket_id, "id_cliente": user["id_cliente"]},
        fetchone=True
    )

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado.")
    if ticket["estado"] != "abierto":
        raise HTTPException(status_code=400, detail="Solo podés editar tickets con estado 'abierto'.")
    if len(body.asunto.strip()) < 3:
        raise HTTPException(status_code=400, detail="El asunto es muy corto.")

    execute(
        """
        UPDATE ticket_soporte
        SET asunto = :asunto, descripcion = :descripcion
        WHERE id_ticket = :id AND id_cliente = :id_cliente
        """,
        {
            "asunto":      body.asunto.strip(),
            "descripcion": body.detalle, 
            "id":          ticket_id,
            "id_cliente":  user["id_cliente"],
        }
    )
    return {"message": "Ticket actualizado correctamente."}


@router.delete("/{ticket_id}")
def eliminar_ticket(ticket_id: int, user: dict = Depends(get_current_user)):
    ticket = query(
        """
        SELECT id_ticket AS id, estado
        FROM ticket_soporte
        WHERE id_ticket = :id AND id_cliente = :id_cliente
        LIMIT 1
        """,
        {"id": ticket_id, "id_cliente": user["id_cliente"]},
        fetchone=True
    )

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado.")
    if ticket["estado"] == "en_proceso":
        raise HTTPException(status_code=400, detail="No podés eliminar un ticket en proceso.")

    execute(
        """
        DELETE FROM ticket_soporte
        WHERE id_ticket = :id AND id_cliente = :id_cliente
        """,
        {"id": ticket_id, "id_cliente": user["id_cliente"]}
    )
    return {"message": "Ticket eliminado correctamente."}
