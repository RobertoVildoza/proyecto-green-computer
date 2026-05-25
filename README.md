# 🌿 Green Computer — Portal del Cliente

> Sistema web para la gestión de contratos de alquiler tecnológico sustentable.  
> Proyecto integrador — Metodologías y Testing — 2026

---

## 👥 Integrantes

| Nombre |
|--------|
| Alam Choquerive |
| Angelo Navarro |
| Fernando Navarro |
| Luciana Torres |
| Roberto Vildoza |
| Lorenzo Zamparini |

---

## 📌 Descripción del sistema

**Green Computer** es una empresa de alquiler de equipos tecnológicos con foco en sustentabilidad. El portal permite a los clientes:

- Iniciar sesión con usuario/contraseña o con Google (Auth0 OAuth)
- Consultar sus contratos de alquiler vigentes y finalizados
- Ver el detalle de los equipos asignados
- Gestionar tickets de soporte (consulta o garantía)
- Visualizar la huella de carbono ahorrada en tiempo real (API Climatiq)
- Gestionar su perfil y cambiar contraseña

---

## 🌐 Demo en producción

| | URL |
|---|---|
| **Frontend** | https://proyecto-green-computer.vercel.app |
| **Backend API** | https://proyecto-green-computer-production.up.railway.app |
| **Documentación API (Swagger)** | https://proyecto-green-computer-production.up.railway.app/docs |

**Credenciales de prueba:** `prueba` / `Test1234!`

---

## 🛠️ Tecnologías utilizadas

| Capa | Tecnología |
|------|-----------|
| **Backend** | Python 3.11 · FastAPI · Uvicorn |
| **Base de datos** | MySQL 8.0 |
| **Autenticación** | JWT (python-jose) · Auth0 (Google OAuth) |
| **Frontend** | HTML5 · CSS3 · JavaScript vanilla |
| **Testing** | Playwright (E2E · API · Mocking · Regresión) |
| **Contenedores** | Docker · Docker Compose |
| **Despliegue** | Railway (backend + DB) · Vercel (frontend) |
| **APIs externas** | Climatiq (huella de carbono) · Auth0 |

---

## 🏗️ Arquitectura del sistema

```
┌─────────────────────┐        ┌──────────────────────┐        ┌────────────────┐
│  Frontend           │  HTTP  │  Backend             │  SQL   │  MySQL 8       │
│  HTML/CSS/JS        │◄──────►│  FastAPI + Uvicorn   │◄──────►│  (Railway)     │
│  (Vercel)           │        │  (Railway)           │        │                │
└─────────────────────┘        └──────────────────────┘        └────────────────┘
                                          │
                              ┌───────────┴───────────┐
                              ▼                       ▼
                    ┌─────────────────┐   ┌─────────────────┐
                    │  Climatiq API   │   │  Auth0 OAuth    │
                    │  (CO₂ cálculo)  │   │  (Google login) │
                    └─────────────────┘   └─────────────────┘
```

---

## ⚙️ Instalación local

### Requisitos previos

- Python 3.11+
- MySQL 8.0
- Node.js 18+
- VS Code con extensión **Live Server**

### 1. Clonar el repositorio

```bash
git clone https://github.com/RobertoVildoza/proyecto-green-computer.git
cd proyecto-green-computer
```

### 2. Configurar variables de entorno

```bash
cp .env.example backend/.env
# Editar backend/.env con los datos reales de la base de datos y claves
```

Ver la sección [Variables de entorno](#️-variables-de-entorno) para el detalle de cada variable.

### 3. Crear la base de datos

Importar el archivo `database_setup.sql` en MySQL (incluye schema + datos de prueba):

```bash
# Linux/macOS
mysql -u root -p < database_setup.sql

# Windows (PowerShell)
Get-Content database_setup.sql | mysql -u root -p
```

O abrirlo directamente con **MySQL Workbench** → File → Open SQL Script → ejecutar con ⚡

### 4. Instalar dependencias del backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 5. Levantar el backend

```bash
uvicorn main:app --reload --port 8000 --host 0.0.0.0
```

- API disponible en: `http://localhost:8000`
- Documentación Swagger: `http://localhost:8000/docs`

### 6. Levantar el frontend

Abrir `frontend/index.html` con **Live Server** en VS Code.  
El frontend queda disponible en `http://localhost:5500`.

---

## 🐳 Instalación con Docker

Requiere Docker Desktop instalado.

```bash
# Levantar backend + MySQL con un solo comando
docker compose up --build

# Detener
docker compose down

# Detener y borrar datos de la base de datos
docker compose down -v
```

Una vez levantado:
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

---

## ☁️ Despliegue en Railway + Vercel

### Backend en Railway

1. Crear cuenta en [railway.app](https://railway.app) e iniciar sesión con GitHub
2. **New Project** → **Deploy from GitHub repo** → seleccionar este repositorio
3. Railway detecta el `Dockerfile` automáticamente
4. Agregar servicio **MySQL**: panel del proyecto → **+ Add** → **Database** → **MySQL**
5. En el servicio del backend → pestaña **Variables** → cargar las variables del `.env.example`
6. En **Settings** → **Networking** → **Generate Domain**
7. Importar `database_setup.sql` al MySQL de Railway con Workbench usando las credenciales del panel

### Frontend en Vercel

1. Crear cuenta en [vercel.com](https://vercel.com) e iniciar sesión con GitHub
2. **New Project** → importar el repositorio
3. Configurar **Root Directory**: `frontend`
4. **Deploy**

> ⚠️ Después del primer despliegue, actualizar `FRONTEND_URL` en Railway con la URL de Vercel, y agregar las URLs de Vercel en el panel de Auth0 (Allowed Callback URLs, Logout URLs, Web Origins).

---

## 🔑 Variables de entorno

Copiar `.env.example` como `backend/.env` y completar los valores. **Nunca subir `.env` al repositorio.**

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `DB_HOST` | Host de MySQL | ✅ |
| `DB_PORT` | Puerto de MySQL (default: 3306) | ✅ |
| `DB_NAME` | Nombre de la base de datos | ✅ |
| `DB_USER` | Usuario de MySQL | ✅ |
| `DB_PASSWORD` | Contraseña de MySQL | ✅ |
| `JWT_SECRET` | Clave secreta para firmar tokens JWT | ✅ |
| `JWT_EXPIRE_MINUTES` | Duración del token en minutos (default: 480) | ✅ |
| `FRONTEND_URL` | URL del frontend para configurar CORS | ✅ |
| `CARBON_API_KEY` | API key de Climatiq para cálculo de CO₂ | ⚠️ opcional |
| `AUTH0_DOMAIN` | Dominio de Auth0 para Google OAuth | ⚠️ opcional |
| `AUTH0_CLIENT_ID` | Client ID de Auth0 | ⚠️ opcional |
| `AUTH0_CLIENT_SECRET` | Client Secret de Auth0 | ⚠️ opcional |
| `AUTH0_AUDIENCE` | Audience de Auth0 | ⚠️ opcional |

---

## 📡 API — Endpoints

Documentación interactiva completa disponible en `/docs` (Swagger UI).

### Autenticación

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `POST` | `/auth/login` | Login con usuario y contraseña | ❌ |
| `POST` | `/auth/register` | Registro de nueva cuenta | ❌ |
| `POST` | `/auth/login-google` | Login con Google (Auth0) | ❌ |
| `POST` | `/auth/forgot-password` | Solicitar código de recuperación | ❌ |
| `POST` | `/auth/reset-password` | Restablecer contraseña con código | ❌ |
| `POST` | `/auth/change-password` | Cambiar contraseña | ✅ |

### Recursos protegidos *(requieren `Authorization: Bearer <token>`)*

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/contratos/mis-contratos` | Lista de contratos del usuario |
| `GET` | `/equipos/mis-equipos` | Equipos alquilados |
| `GET` | `/tickets/mis-tickets` | Tickets de soporte |
| `POST` | `/tickets/nuevo` | Crear nuevo ticket |
| `GET` | `/carbono/mi-huella` | Huella de CO₂ ahorrada |
| `GET` | `/perfil/me` | Datos del usuario actual |

### Sistema

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/health` | Estado de la API y conexión a BD |
| `GET` | `/` | Información de la versión |

---

## 🧪 Tests

### Requisitos

```bash
npm install
npx playwright install chromium
```

> El backend debe estar corriendo en `http://localhost:8000` y el frontend en `http://localhost:5500`.

### Comandos

```bash
# Todos los tests
npx playwright test

# Solo suite de regresión
npx playwright test tests/actividad-3-regresion/

# Solo tests @smoke (rápidos)
npx playwright test --grep @smoke

# Solo tests @regresion
npx playwright test --grep @regresion

# Modo UI interactivo
npm run test:ui

# Ver reporte HTML
npx playwright show-report
```

### Suites incluidas

| Suite | Tipo | Tests | Descripción |
|-------|------|-------|-------------|
| `actividad-1/login.spec.js` | E2E UI | 7 | Flujos de login, logout y navegación |
| `actividad-2/api.spec.js` | API pura | 7 | Tests directos a los endpoints REST |
| `actividad-2/hibrida.spec.js` | Híbrida | 4 | API para arrange + UI para assert |
| `actividad-2/mocking.spec.js` | Mocking | 5 | Intercepción de red con `page.route()` |
| `actividad-3-regresion/regresion.spec.js` | **Regresión** | **14** | Suite de regresión — 5 funcionalidades críticas |

**Resultado suite completa: 38/38 PASS ✅**

### Funcionalidades cubiertas por la regresión

| ID | Funcionalidad | Tests | Resultado |
|----|--------------|-------|-----------|
| FC-01 | Login (válido, inválido, campos vacíos) | 3 | ✅ PASS |
| FC-02 | Logout (limpieza localStorage, redirección) | 2 | ✅ PASS |
| FC-03 | Registro de usuario (alta + login posterior) | 2 | ✅ PASS |
| FC-04 | Validaciones de formulario | 3 | ✅ PASS |
| FC-05 | Protección de rutas autenticadas | 4 | ✅ PASS |

### Tests unitarios — pytest (CRUD de Tickets)

**Requisitos:** backend con venv activo y MySQL corriendo con la base de datos inicializada.

```bash
cd backend
venv\Scripts\activate
pytest test_tickets.py -v
```

| Módulo | Casos | Descripción | Resultado |
|--------|-------|-------------|-----------|
| CREATE | CP-01 a CP-07 | Validaciones de tipo, asunto, campos obligatorios y trim | ✅ 7/7 PASS |
| READ | CP-08 a CP-10 | Listado de tickets, estructura de campos, lista vacía | ✅ 3/3 PASS |
| UPDATE | CP-11 a CP-15 | Edición, ticket inexistente, estado cerrado/en proceso | ✅ 5/5 PASS |
| DELETE | CP-16 a CP-20 | Eliminación, tickets en proceso, smoke test | ✅ 5/5 PASS |
| AISLAMIENTO | CP-21 | Cliente B no puede operar tickets de Cliente A | ✅ 1/1 PASS |
| **TOTAL** | **CP-01 a CP-21** | **Suite completa** | **✅ 21/21 PASS** |
---

## 📁 Estructura del proyecto

```
proyecto-green-computer/
├── backend/
│   ├── main.py                  # App FastAPI, middlewares, CORS
│   ├── database.py              # Conexión MySQL y helpers
│   ├── requirements.txt         # Dependencias Python (versiones fijadas)
│   ├── seed.py                  # Script para poblar datos de prueba
│   ├── routers/
│   │   ├── auth.py              # Login, registro, OAuth, recuperación
│   │   ├── contratos.py         # Contratos de alquiler
│   │   ├── equipos.py           # Equipos alquilados
│   │   ├── tickets.py           # Tickets de soporte
│   │   ├── carbono.py           # Huella de carbono (Climatiq API)
│   │   └── perfil.py            # Perfil del usuario
│   └── utils/
│       ├── auth.py              # JWT helpers, bcrypt
│       └── auth0.py             # Integración Auth0 / Google OAuth
├── frontend/
│   ├── index.html               # Login y registro
│   ├── callback.html            # Callback OAuth de Auth0
│   ├── pages/
│   │   └── dashboard.html       # Dashboard principal
│   ├── js/
│   │   ├── login.js             # Lógica de autenticación
│   │   └── dashboard.js         # Lógica del dashboard
│   └── css/                     # Estilos del portal
├── tests/
│   ├── setup/
│   │   └── health.setup.js      # Verificación del backend antes de correr tests
│   ├── actividad-1/
│   │   └── login.spec.js        # Tests E2E de login
│   ├── actividad-2/
│   │   ├── api.spec.js          # Tests de API pura
│   │   ├── hibrida.spec.js      # Tests híbridos
│   │   └── mocking.spec.js      # Tests con mocking de red
│   └── actividad-3-regresion/
│       └── regresion.spec.js    # Suite de regresión (14 tests)
├── database_setup.sql           # Schema + datos de prueba
├── Dockerfile                   # Imagen Docker del backend
├── docker-compose.yml           # Stack completo local (backend + MySQL)
├── railway.toml                 # Configuración de despliegue en Railway
├── .env.example                 # Plantilla de variables de entorno
├── .gitignore                   # Excluye .env, venv, node_modules, etc.
├── package.json                 # Dependencias Playwright
├── playwright.config.js         # Configuración de tests (workers: 1)
└── README.md
```

---

## 🗄️ Base de datos

El archivo `database_setup.sql` inicializa el schema completo con 6 tablas y datos de prueba:

| Tabla | Descripción |
|-------|-------------|
| `cliente` | Datos de los clientes de Green Computer |
| `usuario_portal` | Credenciales de acceso al portal |
| `equipo` | Catálogo de equipos disponibles |
| `contrato_alquiler` | Contratos de alquiler por cliente |
| `detalle_contrato` | Equipos asignados por contrato |
| `ticket_soporte` | Tickets de soporte técnico |

---

## 🔐 Flujo de autenticación

### Login con usuario/contraseña
```
POST /auth/login → verifica bcrypt → devuelve JWT (8hs) → localStorage
```

### Login con Google (Auth0)
```
Click "Login con Google" → Auth0 → Google → callback.html → POST /auth/login-google
→ verifica email en BD → JWT propio → dashboard
```

---

*Green Computer © 2026 — Tecnología Sustentable*
