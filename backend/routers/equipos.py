from fastapi import APIRouter, Depends, HTTPException # type: ignore
from database import query
from utils.auth import get_current_user

router = APIRouter(prefix="/equipos", tags=["Equipos"])

MANUALS = {
    "ThinkPad X1 Carbon Gen 11": """
        <div class="manual-section">
            <h3>🔋 Batería y Carga</h3>
            <p>El ThinkPad X1 Carbon incluye una batería de 57Wh. Para maximizar su vida útil, cargá entre 20% y 80%. Usá siempre el cargador USB-C de 65W provisto.</p>
        </div>
        <div class="manual-section">
            <h3>⌨️ Atajos de Teclado</h3>
            <ul>
                <li><strong>Fn + F1:</strong> Silenciar micrófono</li>
                <li><strong>Fn + F4:</strong> Suspender equipo</li>
                <li><strong>Fn + F5:</strong> Activar/desactivar Bluetooth</li>
                <li><strong>Fn + F8:</strong> Activar/desactivar Wi-Fi</li>
                <li><strong>Fn + Espacio:</strong> Control de retroiluminación del teclado</li>
            </ul>
        </div>
        <div class="manual-section">
            <h3>🌐 Conectividad</h3>
            <p>Cuenta con Wi-Fi 6E y Bluetooth 5.3. Para conectar a monitores externos, utilizá los puertos Thunderbolt 4 (compatible con DisplayPort y HDMI via adaptador).</p>
        </div>
        <div class="manual-section">
            <h3>🛡️ Cuidados y Garantía</h3>
            <p>Evitá exponer el equipo a temperaturas por encima de 35°C. No cubras las rejillas de ventilación. En caso de cualquier falla de hardware, abrí un ticket de garantía desde el portal.</p>
        </div>
    """,
    "MacBook Pro 14\" M3": """
        <div class="manual-section">
            <h3>🔋 Batería y Carga</h3>
            <p>Batería de 70Wh con hasta 18 horas de autonomía. Cargá con el adaptador MagSafe 3 de 96W incluido. La carga rápida lleva al 50% en 30 minutos.</p>
        </div>
        <div class="manual-section">
            <h3>⌨️ Gestos y Atajos</h3>
            <ul>
                <li><strong>Cmd + Espacio:</strong> Spotlight (búsqueda rápida)</li>
                <li><strong>Cmd + Tab:</strong> Cambiar entre apps</li>
                <li><strong>Cmd + Shift + 4:</strong> Captura de pantalla selectiva</li>
                <li><strong>Control + arriba:</strong> Mission Control</li>
            </ul>
        </div>
        <div class="manual-section">
            <h3>🌐 Conectividad</h3>
            <p>Incluye 3 puertos Thunderbolt 4, HDMI 2.1 y lector SD. Compatible con hasta 2 monitores externos 6K simultáneos.</p>
        </div>
        <div class="manual-section">
            <h3>🛡️ Garantía y Cuidados</h3>
            <p>El equipo está protegido por la garantía Green Computer. No instales software no autorizado. Para cualquier problema, abrí un ticket de garantía desde el portal.</p>
        </div>
    """,
    "Dell XPS 15 9530": """
        <div class="manual-section">
            <h3>🔋 Batería</h3>
            <p>Batería de 86Wh. Cargá con el adaptador de 130W incluido por USB-C o el conector barrel. Tiempo de carga completo: aproximadamente 2 horas.</p>
        </div>
        <div class="manual-section">
            <h3>🖥️ Pantalla OLED</h3>
            <p>La pantalla OLED de 15.6" tiene brillo máximo de 400 nits. Para prolongar su vida útil, evitá imágenes estáticas por más de 2 horas. Activá el salvapantallas automático.</p>
        </div>
        <div class="manual-section">
            <h3>🌐 Conectividad</h3>
            <p>Cuenta con Thunderbolt 4 x2, USB-A 3.1, lector SD y conector 3.5mm. Wi-Fi 6 y Bluetooth 5.2.</p>
        </div>
        <div class="manual-section">
            <h3>🛡️ Garantía</h3>
            <p>Cualquier falla de hardware está cubierta por la garantía Green Computer. Reportá el problema dentro de las 48hs mediante un ticket de garantía en el portal.</p>
        </div>
    """,
    "iMac 27\" M3": """
        <div class="manual-section">
            <h3>⚡ Encendido y Configuración</h3>
            <p>El botón de encendido se encuentra en la parte trasera inferior. Al primer encendido, el Asistente de Configuración te guiará. Usá el ID Apple empresarial provisto por Green Computer.</p>
        </div>
        <div class="manual-section">
            <h3>🖥️ Pantalla y Ajustes</h3>
            <p>Pantalla Retina 5K de 27". Ajustá el brillo en Preferencias del Sistema → Monitores. Activá True Tone para mayor confort visual.</p>
        </div>
        <div class="manual-section">
            <h3>🌐 Conectividad</h3>
            <p>4 puertos USB-A, 2 Thunderbolt 4, ethernet Gigabit integrado y lector SD. Wi-Fi 6E y Bluetooth 5.3.</p>
        </div>
        <div class="manual-section">
            <h3>🛡️ Cuidados</h3>
            <p>No mover el iMac sin apagarlo primero. Limpiar la pantalla solo con el paño incluido ligeramente humedecido. Garantía activa durante todo el contrato.</p>
        </div>
    """,
    "ThinkPad E14 Gen 5": """
        <div class="manual-section">
            <h3>🔋 Batería y Carga</h3>
            <p>Batería de 57Wh con autonomía de hasta 10 horas. Cargá con el adaptador USB-C de 65W incluido. Compatible con carga rápida Rapid Charge de Lenovo.</p>
        </div>
        <div class="manual-section">
            <h3>⌨️ Atajos de Teclado</h3>
            <ul>
                <li><strong>Fn + F1:</strong> Silenciar micrófono</li>
                <li><strong>Fn + F4:</strong> Suspender equipo</li>
                <li><strong>Fn + F5:</strong> Activar/desactivar cámara</li>
                <li><strong>Fn + Espacio:</strong> Control de retroiluminación</li>
            </ul>
        </div>
        <div class="manual-section">
            <h3>🌐 Conectividad</h3>
            <p>2 puertos USB-C, 2 USB-A 3.2, HDMI 2.0 y lector SD. Wi-Fi 6 y Bluetooth 5.1.</p>
        </div>
        <div class="manual-section">
            <h3>🛡️ Garantía</h3>
            <p>Equipo cubierto por garantía Green Computer durante la vigencia del contrato. Cualquier falla reportala mediante un ticket de garantía en el portal.</p>
        </div>
    """,
    "MacBook Air M2": """
        <div class="manual-section">
            <h3>🔋 Batería y Carga</h3>
            <p>Batería de 52.6Wh con hasta 18 horas de autonomía. Cargá con MagSafe 2 de 30W incluido o por USB-C. Diseño sin ventilador: silencioso y fresco en uso normal.</p>
        </div>
        <div class="manual-section">
            <h3>⌨️ Gestos y Atajos</h3>
            <ul>
                <li><strong>Cmd + Espacio:</strong> Spotlight</li>
                <li><strong>Cmd + Shift + 4:</strong> Captura de pantalla selectiva</li>
                <li><strong>Cmd + Tab:</strong> Cambiar entre apps</li>
                <li><strong>Control + arriba:</strong> Mission Control</li>
            </ul>
        </div>
        <div class="manual-section">
            <h3>🌐 Conectividad</h3>
            <p>2 puertos Thunderbolt/USB 4 y MagSafe 2. Para periféricos adicionales usá un hub USB-C. Wi-Fi 6 y Bluetooth 5.3.</p>
        </div>
        <div class="manual-section">
            <h3>🛡️ Garantía y Cuidados</h3>
            <p>Protegido por garantía Green Computer. No instales software no autorizado. Ante cualquier problema, abrí un ticket de garantía desde el portal.</p>
        </div>
    """
}

DEFAULT_MANUAL = """
    <div class="manual-section">
        <h3>📋 Información General</h3>
        <p>Este equipo ha sido verificado y configurado por Green Computer antes de la entrega. Todos los componentes están en óptimas condiciones.</p>
    </div>
    <div class="manual-section">
        <h3>🛡️ Garantía</h3>
        <p>El equipo está cubierto por la garantía Green Computer durante la vigencia del contrato. Para reportar cualquier problema, usá el sistema de tickets del portal.</p>
    </div>
    <div class="manual-section">
        <h3>📞 Soporte</h3>
        <p>Ante cualquier duda, abrí un ticket de consulta y nuestro equipo te responderá en menos de 24 horas hábiles.</p>
    </div>
"""

@router.get("/mis-equipos")
def mis_equipos(user: dict = Depends(get_current_user)):
    """
    Cambios respecto a la versión anterior:
    - tabla equipos             → equipo
    - tabla contratos           → contrato_alquiler + detalle_contrato (tabla intermedia)
    - campo usuario_id          → id_cliente
    - campo e.id                → e.id_equipo AS id       (alias para no romper el JS)
    - campo e.nombre            → e.nombre_equipo AS nombre (alias para no romper el JS)
    - campo e.tipo              → e.categoria AS tipo      (alias para no romper el JS)
    """
    rows = query(
        """
        SELECT DISTINCT
            e.id_equipo                 AS id,
            e.nombre_equipo             AS nombre,
            e.modelo,
            e.categoria                 AS tipo,
            e.fabricante,
            e.specs,
            e.numero_serie
        FROM equipo e
        JOIN detalle_contrato dc    ON dc.id_equipo   = e.id_equipo
        JOIN contrato_alquiler ca   ON ca.id_contrato = dc.id_contrato
        WHERE ca.id_cliente = :id_cliente
          AND ca.estado = 'vigente'
        ORDER BY e.nombre_equipo
        """,
        {"id_cliente": user["id_cliente"]}
    )
    return rows

@router.get("/{equipo_id}/manual")
def get_manual(equipo_id: int, user: dict = Depends(get_current_user)):
    """
    Verifica que el equipo pertenezca a un contrato vigente del usuario
    antes de devolver el manual. Mismo comportamiento que antes.
    """
    equipo = query(
        """
        SELECT
            e.id_equipo                 AS id,
            e.nombre_equipo             AS nombre,
            e.modelo,
            e.categoria                 AS tipo,
            e.specs,
            e.numero_serie
        FROM equipo e
        JOIN detalle_contrato dc    ON dc.id_equipo   = e.id_equipo
        JOIN contrato_alquiler ca   ON ca.id_contrato = dc.id_contrato
        WHERE e.id_equipo   = :id_equipo
          AND ca.id_cliente = :id_cliente
          AND ca.estado     = 'vigente'
        LIMIT 1
        """,
        {"id_equipo": equipo_id, "id_cliente": user["id_cliente"]},
        fetchone=True
    )

    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado o no autorizado.")

    manual_html = MANUALS.get(equipo["nombre"], DEFAULT_MANUAL)

    return {**equipo, "manual_html": manual_html}
