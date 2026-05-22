"""
Etapa 3 - Plan de Pruebas: Gestión de Tickets de Soporte
Green Computer - Portal del Cliente
Casos de prueba: CP-01 a CP-21 (Completos)
"""

import pytest # pyright: ignore[reportMissingImports]
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient # type: ignore
from main import app

client = TestClient(app)

# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------

def get_token(username="prueba", password="Test1234!"):
    response = client.post("/auth/login", json={"username": username, "password": password})
    return response.json()["access_token"]

def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="module")
def token_a():
    return get_token("prueba", "Test1234!")

@pytest.fixture(scope="module")
def token_b():
    return get_token("jperez", "Test1234!")


# ===========================================================================
# OPERACIONES CREATE (CP-01 a CP-07)
# ===========================================================================

class TestCreate:
    def test_cp01_crear_ticket_valido(self, token_a):
        payload = {"tipo": "consulta", "asunto": "Notebook no enciende", "detalle": "...", "equipo_id": 1}
        response = client.post("/tickets/crear", json=payload, headers=auth_headers(token_a))
        assert response.status_code == 200

    def test_cp02_crear_ticket_tipo_garantia(self, token_a):
        payload = {"tipo": "garantia", "asunto": "Pantalla rota", "detalle": "..."}
        response = client.post("/tickets/crear", json=payload, headers=auth_headers(token_a))
        assert response.status_code == 200

    def test_cp03_crear_ticket_tipo_invalido(self, token_a):
        payload = {"tipo": "queja", "asunto": "Invalido", "detalle": "."}
        response = client.post("/tickets/crear", json=payload, headers=auth_headers(token_a))
        assert response.status_code == 400

    def test_cp04_crear_ticket_asunto_muy_corto(self, token_a):
        payload = {"tipo": "consulta", "asunto": "AB", "detalle": "."}
        response = client.post("/tickets/crear", json=payload, headers=auth_headers(token_a))
        assert response.status_code == 400

    def test_cp05_crear_ticket_sin_asunto(self, token_a):
        payload = {"tipo": "consulta", "detalle": "."}
        response = client.post("/tickets/crear", json=payload, headers=auth_headers(token_a))
        assert response.status_code == 422

    def test_cp06_crear_ticket_sin_detalle(self, token_a):
        payload = {"tipo": "consulta", "asunto": "Asunto sin detalle"}
        response = client.post("/tickets/crear", json=payload, headers=auth_headers(token_a))
        assert response.status_code == 422

    @patch("routers.tickets.execute")
    def test_cp07_crear_ticket_asunto_con_espacios(self, mock_execute, token_a):
        payload = {"tipo": "consulta", "asunto": "  Teclado roto  ", "detalle": "."}
        client.post("/tickets/crear", json=payload, headers=auth_headers(token_a))
        
        args, kwargs = mock_execute.call_args
        assert args[1].get("asunto") == "Teclado roto"


# ===========================================================================
# OPERACIONES READ (CP-08 a CP-10)
# ===========================================================================

class TestRead:
    def test_cp08_listar_tickets_del_cliente(self, token_a):
        response = client.get("/tickets/mis-tickets", headers=auth_headers(token_a))
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_cp09_estructura_de_cada_ticket(self, token_a):
        response = client.get("/tickets/mis-tickets", headers=auth_headers(token_a))
        tickets = response.json()
        if len(tickets) > 0:
            campos = {"id", "tipo", "asunto", "detalle", "estado", "fecha_ticket", "equipo_id", "equipo_nombre"}
            for campo in campos: assert campo in tickets[0]

    @patch("routers.tickets.query")
    def test_cp10_cliente_sin_tickets_recibe_lista_vacia(self, mock_query, token_a):
        mock_query.return_value = []
        response = client.get("/tickets/mis-tickets", headers=auth_headers(token_a))
        assert response.json() == []


# ===========================================================================
# OPERACIONES UPDATE (CP-11 a CP-15)
# ===========================================================================

class TestUpdate:
    @patch("routers.tickets.query")
    @patch("routers.tickets.execute")
    def test_cp11_actualizar_ticket_abierto(self, mock_ex, mock_q, token_a):
        mock_q.return_value = {"id": 1, "estado": "abierto"}
        response = client.put("/tickets/1", json={"asunto":"Edit","detalle":"."}, headers=auth_headers(token_a))
        assert response.status_code == 200

    def test_cp12_actualizar_ticket_inexistente(self, token_a):
        response = client.put("/tickets/99999", json={"asunto":"A","detalle":"."}, headers=auth_headers(token_a))
        assert response.status_code == 404

    @patch("routers.tickets.query")
    def test_cp13_no_se_puede_editar_ticket_cerrado(self, mock_q, token_a):
        mock_q.return_value = {"id": 1, "estado": "cerrado"}
        res = client.put("/tickets/1", json={"asunto":"A","detalle":"."}, headers=auth_headers(token_a))
        assert res.status_code == 400

    @patch("routers.tickets.query")
    def test_cp14_regresion_validacion_estado_en_proceso(self, mock_q, token_a):
        mock_q.return_value = {"id": 1, "estado": "en_proceso"}
        res = client.put("/tickets/1", json={"asunto":"A","detalle":"."}, headers=auth_headers(token_a))
        assert res.status_code == 400

    @patch("routers.tickets.query")
    def test_cp15_actualizar_asunto_muy_corto(self, mock_q, token_a):
        mock_q.return_value = {"id": 1, "estado": "abierto"}
        res = client.put("/tickets/1", json={"asunto":"XY","detalle":"."}, headers=auth_headers(token_a))
        assert res.status_code == 400


# ===========================================================================
# OPERACIONES DELETE (CP-16 a CP-20)
# ===========================================================================

class TestDelete:
    @patch("routers.tickets.query")
    @patch("routers.tickets.execute")
    def test_cp16_eliminar_ticket_abierto(self, mock_ex, mock_q, token_a):
        mock_q.return_value = {"id": 1, "estado": "abierto"}
        assert client.delete("/tickets/1", headers=auth_headers(token_a)).status_code == 200

    @patch("routers.tickets.query")
    @patch("routers.tickets.execute")
    def test_cp17_eliminar_ticket_cerrado(self, mock_ex, mock_q, token_a):
        mock_q.return_value = {"id": 1, "estado": "cerrado"}
        assert client.delete("/tickets/1", headers=auth_headers(token_a)).status_code == 200

    def test_cp18_eliminar_ticket_inexistente(self, token_a):
        assert client.delete("/tickets/99999", headers=auth_headers(token_a)).status_code == 404

    @patch("routers.tickets.query")
    def test_cp19_no_se_puede_eliminar_ticket_en_proceso(self, mock_q, token_a):
        mock_q.return_value = {"id": 1, "estado": "en_proceso"}
        assert client.delete("/tickets/1", headers=auth_headers(token_a)).status_code == 400

    def test_cp20_smoke_delete_usa_id_correcto(self, token_a):
        ticket_id = 999
        with patch("routers.tickets.query") as mq, patch("routers.tickets.execute") as me:
            mq.return_value = {"id": ticket_id, "estado": "abierto"}
            client.delete(f"/tickets/{ticket_id}", headers=auth_headers(token_a))
            args, _ = me.call_args
            assert args[1]["id"] == ticket_id
            assert "id_cliente" in args[1], "El DELETE no filtra por id_cliente"


# ===========================================================================
# AISLAMIENTO (SEGURIDAD CRÍTICA) — CP-21
# ===========================================================================

class TestAislamiento:
    def test_cp21_cliente_b_no_puede_operar_tickets_de_cliente_a(self, token_a, token_b):
        """
        CP-21: Triple validación de aislamiento (READ, UPDATE, DELETE).
        Verifica que el Cliente B no tiene acceso a los recursos del Cliente A.
        """
        # 1. Preparación: Cliente A crea un ticket privado
        res = client.post("/tickets/crear", json={"tipo":"consulta","asunto":"Privado A","detalle":"."}, headers=auth_headers(token_a))
        tid_a = res.json()["id"]

        # ACCIÓN 1: Intento de LECTURA (B no debe ver el ticket de A)
        res_read = client.get("/tickets/mis-tickets", headers=auth_headers(token_b))
        assert tid_a not in [t["id"] for t in res_read.json()], "Error: Cliente B puede ver ticket de A"

        # ACCIÓN 2: Intento de EDICIÓN (B no debe poder modificar ticket de A)
        res_put = client.put(f"/tickets/{tid_a}", json={"asunto":"Hacked","detalle":"."}, headers=auth_headers(token_b))
        assert res_put.status_code in (403, 404), "Error: Cliente B pudo editar ticket de A"

        # ACCIÓN 3: Intento de ELIMINACIÓN (B no debe poder borrar ticket de A)
        res_del = client.delete(f"/tickets/{tid_a}", headers=auth_headers(token_b))
        assert res_del.status_code in (403, 404), "Error: Cliente B pudo borrar ticket de A"