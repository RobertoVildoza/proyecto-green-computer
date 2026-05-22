from fastapi import APIRouter, Depends # type: ignore
from database import query
from utils.auth import get_current_user
import httpx, os # type: ignore
from datetime import date
from dotenv import load_dotenv # type: ignore

load_dotenv()

router = APIRouter(prefix="/carbono", tags=["Carbono"])

CARBON_API_KEY = os.getenv("CARBON_API_KEY", "")

CLIMATIQ_URL = "https://api.climatiq.io/data/v1/estimate"

CO2_POR_TIPO = {
    "notebook": 300.0,
    "desktop":  500.0,
}

VIDA_UTIL_DIAS = {
    "notebook": 4 * 365,
    "desktop":  5 * 365,
}

KWH_POR_DIA = {
    "notebook": 0.05,
    "desktop":  0.15,
}

async def calcular_co2_climatiq(tipo_equipo: str, dias: int) -> float:
    if not CARBON_API_KEY or CARBON_API_KEY == "tu_api_key_de_carbon_interface":
        return calcular_co2_local(tipo_equipo, dias)

    try:
        kwh_total = KWH_POR_DIA.get(tipo_equipo, 0.05) * dias

        payload = {
            "emission_factor": {
                "activity_id": "electricity-supply_grid-source_supplier_mix",
                "region": "AR",
                "data_version": "^3"
            },
            "parameters": {
                "energy": kwh_total,
                "energy_unit": "kWh"
            }
        }

        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.post(
                CLIMATIQ_URL,
                headers={
                    "Authorization": f"Bearer {CARBON_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=payload
            )

            if res.status_code == 200:
                data = res.json()
                co2_uso = data.get("co2e", 0)

                co2_fab       = CO2_POR_TIPO.get(tipo_equipo, 300)
                vida_util     = VIDA_UTIL_DIAS.get(tipo_equipo, 1460)
                co2_fab_fracc = co2_fab * (dias / vida_util)

                total = round(co2_uso + co2_fab_fracc, 3)
                print(f"[Climatiq] {tipo_equipo} {dias}d → uso={co2_uso:.3f}kg fab={co2_fab_fracc:.3f}kg total={total}kg")
                return total
            else:
                print(f"[Climatiq Error] {res.status_code}: {res.text}")

    except Exception as e:
        print(f"[Climatiq Exception] {e}")

    return calcular_co2_local(tipo_equipo, dias)

def calcular_co2_local(tipo_equipo: str, dias: int) -> float:
    co2_total = CO2_POR_TIPO.get(tipo_equipo, 300)
    vida_util  = VIDA_UTIL_DIAS.get(tipo_equipo, 1460)
    return round(co2_total * (dias / vida_util), 3)

def usar_api() -> bool:
    return bool(CARBON_API_KEY and CARBON_API_KEY not in ("", "tu_api_key_de_carbon_interface"))

@router.get("/mi-huella")
async def mi_huella(user: dict = Depends(get_current_user)):
    contratos = query(
        """
        SELECT
            ca.id_contrato                  AS id,
            ca.fecha_inicio,
            ca.fecha_vencim                 AS fecha_fin,
            ca.estado,
            e.nombre_equipo                 AS nombre,
            e.modelo,
            e.categoria                     AS tipo
        FROM contrato_alquiler ca
        JOIN detalle_contrato dc ON dc.id_contrato = ca.id_contrato
        JOIN equipo e            ON e.id_equipo    = dc.id_equipo
        WHERE ca.id_cliente = :id_cliente
        """,
        {"id_cliente": user["id_cliente"]}
    )

    equipos_detalle = []
    total_kg = 0.0

    for c in contratos:
        inicio = c["fecha_inicio"]
        fin    = c["fecha_fin"] or date.today()
        if hasattr(inicio, "date"): inicio = inicio.date()
        if hasattr(fin,   "date"): fin    = fin.date()

        dias = max((fin - inicio).days, 1)
        kg   = await calcular_co2_climatiq(c["tipo"], dias)
        total_kg += kg

        equipos_detalle.append({
            "nombre":         c["nombre"],
            "modelo":         c["modelo"],
            "tipo":           c["tipo"],
            "dias_alquilado": dias,
            "estado":         c["estado"],
            "kg_co2":         kg
        })

    return {
        "total_kg_co2": round(total_kg, 2),
        "equipos":      equipos_detalle,
        "fuente":       "Climatiq API (electricidad AR + ciclo de vida)" if usar_api() else "Cálculo local (ciclo de vida)",
        "metodologia":  "CO2 por consumo eléctrico del equipo durante el alquiler + fracción de fabricación evitada al no comprar un equipo nuevo."
    }
