# Informe de Cierre — Proyecto Green Computer

**Materia:** Metodología y Testing
**Fecha de entrega:** Martes 9 de junio de 2026
**Repositorio:** https://github.com/RobertoVildoza/proyecto-green-computer
**Integrantes:** Alam Choquerive · Angelo Navarro · Fernando Navarro · Luciana Torres · Roberto Vildoza · Lorenzo Zamparini

---

## 1. Descripción del Proyecto

**Green Computer** es un portal web para clientes de una empresa de alquiler de tecnología con foco en la sustentabilidad. El sistema permite a los clientes:

- Iniciar sesión con usuario/contraseña o con Google (OAuth mediante Auth0)
- Consultar sus contratos de alquiler vigentes y finalizados
- Ver el detalle de los equipos alquilados
- Gestionar tickets de soporte (consulta o garantía)
- Visualizar la huella de carbono ahorrada en tiempo real (integración con Climatiq API)
- Cambiar su contraseña y gestionar su perfil

El proyecto se desarrolló en cinco etapas iterativas a lo largo del año, aplicando prácticas de testing de forma incremental en cada una.

---

## 2. Avances por Etapa

### Etapa 1 — Relevamiento y Planificación

- Definición del dominio: portal de clientes para una empresa de tecnología sustentable
- Diseño del modelo de datos relacional (MySQL)
- Identificación de los casos de uso principales (login, contratos, tickets, carbono)
- Primeros wireframes del portal

> **Entregable:** Carpeta de proyecto inicial con casos de uso y modelo de datos.

---

### Etapa 2 — Desarrollo del Backend

- Implementación de la API REST con FastAPI
- Módulos desarrollados: autenticación JWT, contratos, equipos, tickets, huella de carbono y perfil
- Integración con la API de Climatiq para el cálculo de CO₂
- Base de datos MySQL con script de inicialización y datos de prueba (`seed.py`)
- Integración con Auth0 para el login social con Google

> **Entregable:** API funcional con documentación automática en `/docs`.

---

### Etapa 3 — Desarrollo del Frontend

- Implementación del portal en HTML/CSS/JavaScript vanilla
- Pantallas: login, registro, recuperación de contraseña y dashboard
- Integración con el backend mediante fetch / API REST
- Autenticación con JWT almacenado en localStorage
- Flujo de OAuth con callback para Google

> **Entregable:** Frontend funcional integrado con el backend.

---

### Etapa 4 — Testing (Actividades 1 y 2)

En esta etapa se desarrollaron las primeras suites de pruebas automatizadas con Playwright, que fueron expuestas en clase. Cabe aclarar que la entrega formal y consolidada de todo el testing corresponde a la Etapa 5; en la Etapa 4 se trabajó sobre las Actividades 1 y 2.

**Actividad 1 — Tests E2E de Login (`login.spec.js`)**
- Pruebas de login exitoso, login fallido y validaciones de formulario
- Tests de interfaz de usuario automatizados con Playwright

**Actividad 2 — Tests de API (`api.spec.js`)**
- Pruebas directas a los endpoints REST (sin UI)
- Cobertura de autenticación, endpoints protegidos y manejo de errores

**Actividad 2 — Tests Híbridos (`hibrida.spec.js`)**
- Combinación de llamadas API para preparar el estado (arrange eficiente)
- Verificación de resultados a través de la UI

**Actividad 2 — Tests con Mocking (`mocking.spec.js`)**
- Intercepción de llamadas de red con `page.route()`
- Simulación de respuestas del backend para aislar el frontend
- Pruebas de protección de rutas y comportamiento con datos mock

> **Entregable:** Suites de tests con reportes HTML y evidencia en screenshots.

---

### Etapa 5 — Release Candidate, Regresión y Despliegue

**Suite de regresión (`regresion.spec.js`)**

Se desarrolló una suite completa que cubre las funcionalidades críticas del sistema. La suite se organiza en 5 funcionalidades críticas (FC-01 a FC-05), cada una compuesta por uno o más casos de prueba individuales (REG-01 a REG-14):

| FC | Caso | Descripción | Resultado |
|------|--------|---------------|-----------|
| FC-01 | REG-01 | Login con credenciales válidas redirige al dashboard | ✅ PASS |
| FC-01 | REG-02 | Login con contraseña incorrecta muestra error y no redirige | ✅ PASS |
| FC-01 | REG-03 | Campos vacíos muestran validación sin llamar al backend | ✅ PASS |
| FC-02 | REG-04 | Cerrar sesión limpia localStorage y redirige al login | ✅ PASS |
| FC-02 | REG-05 | Acceder al dashboard sin token redirige al login | ✅ PASS |
| FC-03 | REG-06 | Registro con datos válidos completos crea la cuenta | ✅ PASS |
| FC-03 | REG-07 | Usuario registrado puede iniciar sesión correctamente | ✅ PASS |
| FC-04 | REG-08 | Contraseña con menos de 8 caracteres genera error | ✅ PASS |
| FC-04 | REG-09 | Contraseñas que no coinciden generan error | ✅ PASS |
| FC-04 | REG-10 | Campos obligatorios vacíos generan error | ✅ PASS |
| FC-05 | REG-11 | Sin token, GET /contratos/mis-contratos devuelve 401 | ✅ PASS |
| FC-05 | REG-12 | Con token válido, GET /contratos/mis-contratos devuelve 200 | ✅ PASS |
| FC-05 | REG-13 | Token malformado en localStorage no permite acceso | ✅ PASS |
| FC-05 | REG-14 | Logout elimina token y redirige correctamente | ✅ PASS |

**Resultado de la suite completa de Playwright: 38/38 PASS ✅**

**Tests unitarios con pytest (CRUD de Tickets)**

De forma complementaria, el módulo de Tickets cuenta con 21 tests unitarios automatizados con pytest (CP-01 a CP-21) que cubren las operaciones CREATE, READ, UPDATE, DELETE y el aislamiento entre clientes. Resultado: **21/21 PASS ✅**

**Preparación para despliegue**

- `Dockerfile` para la containerización del backend
- `docker-compose.yml` para el entorno de desarrollo local (backend + MySQL)
- `railway.toml` para el despliegue en Railway
- Documentación de despliegue en Railway (backend + base de datos) y Vercel (frontend)

> **Entregable:** Software en condición de release, documentación completa y reporte de regresión con evidencia de ejecución.

---

## 3. Arquitectura Final

La solución sigue una arquitectura de tres capas desacopladas, con el frontend y el backend desplegados de forma independiente y dos servicios externos integrados.

```
Frontend (Vercel)          Backend (Railway)         Base de Datos (Railway)
─────────────────    →     ──────────────────    →   ───────────────────────
HTML / CSS / JS            FastAPI + Uvicorn          MySQL 8.0
index.html                 /auth/*                    cliente
dashboard.html             /contratos/*               usuario_portal
callback.html              /equipos/*                 equipo
                           /tickets/*                 contrato_alquiler
                           /carbono/*                 detalle_contrato
                           /perfil/*                  ticket_soporte
```

**Servicios externos integrados:** Climatiq API (cálculo de huella de carbono) y Auth0 (login social con Google OAuth).

---

## 4. Métricas del Proyecto

| Métrica | Valor |
|---------|-------|
| Endpoints de API | 12 |
| Tablas en la base de datos | 6 |
| Tests automatizados | 59 (38 Playwright + 21 pytest) |
| Suites de testing | 5 |
| Tipos de tests aplicados | E2E · API · Mocking · Híbrido · Regresión |
| Herramientas de testing | Playwright · pytest |
| Cobertura de flujos críticos | Login · Registro · Logout · Contratos · Seguridad |

---

## 5. Lecciones Aprendidas

### Técnicas

**Separación de responsabilidades en los tests.** Al combinar tests de API pura con tests de UI (patrón híbrido) se logró una suite más eficiente: la preparación del estado se hace por API (rápido y confiable) y la verificación por UI (realista). Esto redujo el tiempo total de ejecución frente a hacer todo por UI.

**Mocking como herramienta de aislamiento.** El uso de `page.route()` en Playwright permitió probar el frontend de forma independiente del backend, lo que resultó especialmente útil para simular errores del servidor y estados difíciles de reproducir con datos reales.

**Parámetros con nombre en SQL.** El helper `_convert_params()` en `database.py`, que convierte `:nombre` a `%s` para MySQL, mejoró notablemente la legibilidad del código SQL a lo largo del proyecto.

**Docker para la reproducibilidad.** Containerizar el backend desde etapas tempranas habría facilitado la configuración del entorno en las primeras semanas; quedó como tarea de la etapa final.

### De proceso

**Valor de los tests de regresión.** Al agregar funcionalidades en etapas tardías (Auth0, cambio de contraseña), la suite de regresión permitió verificar de inmediato que el flujo de login básico seguía funcionando. Sin esa suite, esa verificación debería hacerse manualmente.

**Gestión de secretos.** Durante el desarrollo se comprendió la importancia de mantener las credenciales fuera del repositorio. La práctica correcta es incluir `.env` en el `.gitignore` desde el primer commit y usar `.env.example` como plantilla de referencia, tal como quedó finalmente configurado el proyecto.

**Variables de entorno en producción.** Railway gestiona las variables de entorno de forma segura desde su panel, lo que simplifica el despliegue sin manejar archivos de configuración sensibles en producción.

---

## 6. Herramientas Utilizadas

| Herramienta | Uso |
|-------------|-----|
| Python 3.11 + FastAPI | Backend REST |
| MySQL 8.0 | Base de datos relacional |
| Playwright | Testing E2E, API, mocking y regresión |
| pytest | Tests unitarios del CRUD de tickets |
| Docker + Docker Compose | Containerización y entorno local |
| Railway | Despliegue del backend y la base de datos |
| Vercel | Despliegue del frontend estático |
| Auth0 | Login social con Google OAuth |
| Climatiq API | Cálculo de la huella de carbono |
| GitHub | Control de versiones |
| VS Code + Live Server | Desarrollo del frontend |

---

## 7. Datos de Entrega

| Recurso | Enlace / Ubicación |
|---------|--------------------|
| Repositorio | https://github.com/RobertoVildoza/proyecto-green-computer |
| Backend en producción | https://proyecto-green-computer-production.up.railway.app |
| Frontend en producción | https://proyecto-green-computer.vercel.app |
| Documentación API (Swagger) | https://proyecto-green-computer-production.up.railway.app/docs |
| Credenciales de prueba | `prueba` / `Test1234!` |
| Video de prueba UI automatizada | Adjunto en la entrega (prueba E2E con Playwright) |
| Evidencia de ejecución | Capturas de Playwright (38/38) y pytest (21/21) en el anexo |

---

*Green Computer © 2026 — Tecnología Sustentable*
