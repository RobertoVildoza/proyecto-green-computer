# 🌿 Green Computer — Portal del Cliente

Portal web para clientes de **Green Computer**, empresa de alquiler de tecnología sustentable. Permite gestionar contratos, equipos, tickets de soporte y visualizar la huella de carbono ahorrada.

## 🌐 Demo en producción

| | URL |
|---|---|
| **Frontend** | https://proyecto-green-computer.vercel.app |
| **API** | https://proyecto-green-computer-production.up.railway.app |
| **Documentación API** | https://proyecto-green-computer-production.up.railway.app/docs |

**Usuario de prueba:** `prueba` / `Test1234!`

---

## Índice

- [Tecnologías](#tecnologías)
- [Arquitectura](#arquitectura)
- [Instalación local](#instalación-local)
- [Instalación con Docker](#instalación-con-docker)
- [Despliegue en Railway + Vercel](#despliegue-en-railway--vercel)
- [Variables de entorno](#variables-de-entorno)
- [API — Endpoints](#api--endpoints)
- [Tests](#tests)
- [Estructura del proyecto](#estructura-del-proyecto)

---

## Tecnologías

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.11 · FastAPI · Uvicorn |
| Base de datos | MySQL 8.0 |
| Autenticación | JWT (python-jose) · Auth0 (Google OAuth) |
| Frontend | HTML5 · CSS3 · JavaScript vanilla |
| Tests | Playwright (E2E + API + mocking) · pytest |
| Contenedores | Docker · Docker Compose |
| CI/Despliegue | Railway (backend + DB) · Vercel (frontend) |

---

## Arquitectura

```
┌─────────────────┐        ┌──────────────────┐        ┌──────────┐
│  Frontend       │  HTTP  │  Backend         │  SQL   │  MySQL   │
│  (Vercel)       │◄──────►│  FastAPI         │◄──────►│ (Railway)│
│  HTML/CSS/JS    │        │  (Railway)       │        │          │
└─────────────────┘        └──────────────────┘        └──────────┘
                                    │
                                    ▼
                           ┌──────────────────┐
                           │  APIs externas   │
                           │  · Climatiq CO2  │
                           │  · Auth0 OAuth   │
                           └──────────────────┘
```

---

## Instalación local

### Requisitos previos

- Python 3.11+
- MySQL 8.0
- Node.js 18+ (solo para tests Playwright)
- Extensión **Live Server** en VS Code (para el frontend)

### 1. Clonar el repositorio

```bash
git clone https://github.com/RobertoVildoza/proyecto-green-computer.git
cd proyecto-green-computer
```

### 2. Configurar variables de entorno

```bash
cp .env.example backend/.env
# Editar backend/.env con tus datos reales
```

### 3. Crear la base de datos

```bash
mysql -u root -p < database_setup.sql
```

### 4. Instalar dependencias del backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Levantar el backend

```bash
uvicorn main:app --reload --port 8000
```

La API queda disponible en `http://localhost:8000`  
Documentación interactiva: `http://localhost:8000/docs`

### 6. Levantar el frontend

Abrí `frontend/index.html` con **Live Server** en VS Code (botón derecho → *Open with Live Server*).  
El frontend queda en `http://localhost:5500`.

---

## Instalación con Docker

```bash
docker compose up --build
```

Levanta backend FastAPI en el puerto 8000 y MySQL en el 3306, inicializado con `database_setup.sql`.

```bash
docker compose down        # detener
docker compose down -v     # detener y borrar datos
```

---

## Despliegue en Railway + Vercel

### Backend en Railway

1. [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Agregar servicio MySQL desde el panel
3. Cargar variables de entorno del `.env.example` en la pestaña Variables
4. Ejecutar `database_setup.sql` conectándose al MySQL de Railway con Workbench o similar

### Frontend en Vercel

1. [vercel.com](https://vercel.com) → New Project → importar repo
2. Root Directory: `frontend`
3. Deploy

---

## Variables de entorno

Ver `.env.example` para la lista completa.

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `DB_HOST` | Host de MySQL | ✅ |
| `DB_PORT` | Puerto de MySQL | ✅ |
| `DB_NAME` | Nombre de la base de datos | ✅ |
| `DB_USER` | Usuario de MySQL | ✅ |
| `DB_PASSWORD` | Contraseña de MySQL | ✅ |
| `JWT_SECRET` | Clave secreta para tokens JWT | ✅ |
| `CARBON_API_KEY` | API key de Climatiq | ⚠️ opcional |
| `AUTH0_DOMAIN` | Dominio de Auth0 | ⚠️ opcional |
| `AUTH0_CLIENT_ID` | Client ID de Auth0 | ⚠️ opcional |
| `AUTH0_CLIENT_SECRET` | Client Secret de Auth0 | ⚠️ opcional |

---

## API — Endpoints

Documentación completa en `/docs` (Swagger UI).

### Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/auth/login` | Login con usuario y contraseña |
| `POST` | `/auth/register` | Registro de nueva cuenta |
| `POST` | `/auth/login-google` | Login con Google (Auth0) |
| `POST` | `/auth/forgot-password` | Solicitar código de recuperación |
| `POST` | `/auth/reset-password` | Restablecer contraseña |
| `POST` | `/auth/change-password` | Cambiar contraseña *(auth)* |

### Recursos *(requieren token)*

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/contratos/mis-contratos` | Contratos del usuario |
| `GET` | `/equipos/mis-equipos` | Equipos alquilados |
| `GET` | `/tickets/mis-tickets` | Tickets de soporte |
| `POST` | `/tickets/nuevo` | Crear ticket |
| `GET` | `/carbono/mi-huella` | Huella de CO₂ |
| `GET` | `/perfil/me` | Perfil del usuario |
| `GET` | `/health` | Estado de la API |

---

## Tests

```bash
npm install
npx playwright install chromium
npx playwright test                              # todos los tests
npx playwright test tests/actividad-3-regresion/ # solo regresión
npx playwright show-report                       # ver reporte HTML
```

| Suite | Tipo | Archivo |
|-------|------|---------|
| actividad-1 | E2E Login UI | `login.spec.js` |
| actividad-2 | API pura | `api.spec.js` |
| actividad-2 | Híbrida | `hibrida.spec.js` |
| actividad-2 | Mocking | `mocking.spec.js` |
| actividad-3 | **Regresión** | `regresion.spec.js` |

---

## Estructura del proyecto

```
proyecto-green-computer/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── requirements.txt
│   ├── routers/          # auth, contratos, equipos, tickets, carbono, perfil
│   └── utils/            # JWT, Auth0
├── frontend/
│   ├── index.html
│   ├── callback.html
│   ├── pages/
│   └── js/               # login.js, dashboard.js
├── tests/
│   ├── actividad-1/
│   ├── actividad-2/
│   └── actividad-3-regresion/
├── database_setup.sql
├── Dockerfile
├── docker-compose.yml
├── railway.toml
├── .env.example
└── README.md
```
