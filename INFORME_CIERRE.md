# Informe de Cierre — Proyecto Green Computer

**Materia:** Calidad de Software / Testing  
**Fecha de cierre:** Junio 2026  
**Repositorio:** https://github.com/RobertoVildoza/proyecto-green-computer

---

## 1. Descripción del Proyecto

**Green Computer** es un portal web para clientes de una empresa de alquiler de tecnología sustentable. El sistema permite a los clientes:

- Iniciar sesión con usuario/contraseña o con Google (OAuth via Auth0)
- Consultar sus contratos de alquiler vigentes
- Ver el detalle de los equipos alquilados
- Gestionar tickets de soporte
- Visualizar su huella de carbono ahorrada (integración con Climatiq API)
- Cambiar su contraseña y gestionar su perfil

El proyecto fue desarrollado en cinco etapas iterativas a lo largo del cuatrimestre, aplicando prácticas de testing en cada una.

---

## 2. Avances por Etapa

### Etapa 1 — Relevamiento y Planificación

- Definición del dominio: portal de clientes para empresa de tecnología sustentable
- Diseño del modelo de datos relacional (MySQL)
- Identificación de casos de uso principales (login, contratos, tickets, carbono)
- Primeros wireframes del portal

**Entregable:** Carpeta de proyecto inicial con casos de uso y modelo de datos

---

### Etapa 2 — Desarrollo del Backend

- Implementación de la API REST con FastAPI
- Módulos desarrollados: autenticación JWT, contratos, equipos, tickets, huella de carbono, perfil
- Integración con la API de Climatiq para cálculo de CO2
- Base de datos MySQL con script de inicialización y datos de prueba (`seed.py`)
- Integración con Auth0 para login social con Google

**Entregable:** API funcional con documentación automática en `/docs`

---

### Etapa 3 — Desarrollo del Frontend

- Implementación del portal HTML/CSS/JS vanilla
- Pantallas: login, registro, recuperación de contraseña, dashboard
- Integración con el backend via fetch/API REST
- Autenticación con JWT almacenado en localStorage
- Flujo de OAuth con callback para Google

**Entregable:** Frontend funcional integrado con el backend

---

### Etapa 4 — Testing (Actividades 1 y 2)

Se desarrollaron tres suites de tests con Playwright:

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

**Entregable:** Suite de tests con reportes HTML y evidencia en video/screenshots

---

### Etapa 5 — Release Candidate, Regresión y Despliegue

**Tests de Regresión (`regresion.spec.js`)**

Se desarrolló una suite completa de regresión que cubre los flujos críticos del sistema:

| ID | Caso de Prueba | Resultado |
|----|---------------|-----------|
| REG-01 | Login con credenciales válidas redirige al dashboard | ✅ PASS |
| REG-02 | Login con contraseña incorrecta muestra error | ✅ PASS |
| REG-03 | Campos vacíos muestran validación sin llamar al backend | ✅ PASS |
| REG-04 | Cerrar sesión limpia localStorage y redirige al login | ✅ PASS |
| REG-05 | Acceder al dashboard sin token redirige al login | ✅ PASS |
| REG-06 | Registro con datos válidos crea la cuenta | ✅ PASS |
| REG-07 | Usuario registrado puede iniciar sesión | ✅ PASS |
| REG-08 | Contraseña menor a 8 caracteres genera error | ✅ PASS |
| REG-09 | Contraseñas que no coinciden generan error | ✅ PASS |
| REG-10 | Campos obligatorios vacíos generan error | ✅ PASS |
| REG-11 | Sin token, GET /contratos devuelve 401 | ✅ PASS |
| REG-12 | Con token válido, GET /contratos devuelve 200 | ✅ PASS |
| REG-13 | Token malformado no permite acceso | ✅ PASS |
| REG-14 | Logout elimina token y redirige correctamente | ✅ PASS |

**Preparación para despliegue**

- `Dockerfile` para containerización del backend
- `docker-compose.yml` para entorno de desarrollo local
- `railway.toml` para despliegue en Railway
- Documentación de despliegue en Railway (backend) + Vercel (frontend)

**Entregable:** Software en condición de release, documentación completa, reporte de regresión

---

## 3. Arquitectura Final

```
Frontend (Vercel)          Backend (Railway)         Base de Datos (Railway)
─────────────────    →     ──────────────────    →   ───────────────────────
HTML / CSS / JS            FastAPI + Uvicorn          MySQL 8.0
index.html                 /auth/*                    cliente
dashboard.html             /contratos/*               usuario_portal
                           /equipos/*                 equipo
                           /tickets/*                 contrato_alquiler
                           /carbono/*                 detalle_contrato
                           /perfil/*                  ticket_soporte
```

---

## 4. Métricas del Proyecto

| Métrica | Valor |
|---------|-------|
| Endpoints de API | 12 |
| Tablas en la base de datos | 6 |
| Tests automatizados | 30+ |
| Suites de testing | 5 |
| Tipos de tests aplicados | E2E · API · Mocking · Híbrido · Regresión |
| Herramientas de testing | Playwright · pytest |
| Cobertura de flujos críticos | Login · Registro · Logout · Contratos · Seguridad |

---

## 5. Lecciones Aprendidas

### Técnicas

**Separación de responsabilidades en los tests**
Al combinar tests de API pura con tests de UI (patrón híbrido), se logró una suite más eficiente: la preparación del estado se hace por API (rápido y confiable) y la verificación por UI (realista). Esto redujo el tiempo total de ejecución respecto a hacer todo por UI.

**Mocking como herramienta de aislamiento**
El uso de `page.route()` en Playwright permitió probar el frontend de forma independiente del backend. Esto fue especialmente útil para simular errores del servidor y estados que son difíciles de reproducir con datos reales.

**Parámetros con nombre en SQL**
El helper `_convert_params()` en `database.py`, que convierte `:nombre` a `%s` para MySQL, fue una decisión que mejoró mucho la legibilidad del código SQL a lo largo del proyecto.

**Docker para reproducibilidad**
Containerizar el backend desde etapas tempranas habría facilitado la configuración del entorno en las primeras semanas. Quedó como una tarea de la etapa final.

### De proceso

**Valor de los tests de regresión**
Al agregar funcionalidades en etapas tardías (Auth0, cambio de contraseña), los tests de regresión detectaron inmediatamente que el flujo de login básico seguía funcionando correctamente. Sin esta suite, ese tipo de verificación se haría manualmente.

**El `.env` en el repositorio**
Las credenciales reales estuvieron expuestas en el repositorio durante el desarrollo. Para un proyecto real, esto representaría un problema de seguridad crítico. La solución correcta es agregar `.env` al `.gitignore` desde el primer commit y usar `.env.example` como referencia.

**Variables de entorno en Railway**
Railway gestiona las variables de entorno de forma segura a través de su panel, lo que simplifica mucho el despliegue sin necesidad de manejar archivos de configuración en producción.

---

## 6. Herramientas Utilizadas

| Herramienta | Uso |
|-------------|-----|
| Python 3.11 + FastAPI | Backend REST |
| MySQL 8.0 | Base de datos relacional |
| Playwright | Testing E2E automatizado |
| Docker + Docker Compose | Containerización y entorno local |
| Railway | Despliegue del backend y base de datos |
| Vercel | Despliegue del frontend estático |
| Auth0 | Login social con Google OAuth |
| Climatiq API | Cálculo de huella de carbono |
| GitHub | Control de versiones |
| VS Code + Live Server | Desarrollo del frontend |

---

## 7. Instrucciones de Entrega

- **Repositorio:** https://github.com/RobertoVildoza/proyecto-green-computer
- **Backend en producción:** `https://proyecto-green-computer-production.up.railway.app`
- **Frontend en producción:** `https://proyecto-green-computer.vercel.app`
- **Video de prueba UI automatizada:** ver carpeta `playwright-report/` o adjunto separado
- **Documentación API:** `https://proyecto-green-computer-production.up.railway.app/docs`
