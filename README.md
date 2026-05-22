# 🌿 Green Computer — Portal del Cliente

Portal web para clientes de **Green Computer**, empresa de alquiler de tecnología sustentable. Permite gestionar contratos, equipos, tickets de soporte y visualizar la huella de carbono ahorrada.

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
│  (Vercel)       │◄──────►│  FastAPI         │◄──────►│  (Railway│
│  HTML/CSS/JS    │        │  (Railway)       │        │   DB)    │
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

### Requisitos

- Docker Desktop instalado

### Levantar todo con un comando

```bash
# Desde la raíz del proyecto
docker compose up --build
```

Esto levanta:
- **MySQL** en el puerto 3306 (inicializado con `database_setup.sql`)
- **Backend FastAPI** en el puerto 8000

Para detener:
```bash
docker compose down
```

Para borrar también los datos de la base de datos:
```bash
docker compose down -v
```

---

## Despliegue en Railway + Vercel

### Backend en Railway

1. Crear cuenta en [railway.app](https://railway.app)
2. Nuevo proyecto → **Deploy from GitHub repo** → seleccionar este repositorio
3. Railway detecta el `Dockerfile` automáticamente
4. Agregar un servicio **MySQL** desde el panel de Railway
5. En el servicio del backend, ir a **Variables** y cargar todas las del `.env.example`:
   - `DB_HOST` → hostname que te da Railway para el MySQL
   - `DB_PORT` → puerto que te da Railway (normalmente no es 3306)
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD` → credenciales del MySQL de Railway
   - `JWT_SECRET`, `CARBON_API_KEY`, etc.
6. En **Settings → Networking** → generar un dominio público
7. Correr el script de base de datos conectándose al MySQL de Railway desde un cliente (TablePlus, DBeaver, etc.) usando las credenciales del panel

### Frontend en Vercel

1. Crear cuenta en [vercel.com](https://vercel.com)
2. **Add New Project** → importar el mismo repositorio de GitHub
3. En la configuración del proyecto:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Other
4. En `frontend/js/dashboard.js` y `frontend/js/login.js`, reemplazar `http://localhost:8000` por la URL pública de Railway
5. Deploy → Vercel genera una URL pública automáticamente

---

## Variables de entorno

Todas las variables necesarias están documentadas en `.env.example`.

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `DB_HOST` | Host de MySQL | ✅ |
| `DB_PORT` | Puerto de MySQL (default 3306) | ✅ |
| `DB_NAME` | Nombre de la base de datos | ✅ |
| `DB_USER` | Usuario de MySQL | ✅ |
| `DB_PASSWORD` | Contraseña de MySQL | ✅ |
| `JWT_SECRET` | Clave secreta para firmar tokens JWT | ✅ |
| `JWT_EXPIRE_MINUTES` | Duración del token en minutos (default 480) | ✅ |
| `CARBON_API_KEY` | API key de Climatiq para cálculo de CO2 | ⚠️ opcional |
| `AUTH0_DOMAIN` | Dominio de Auth0 para Google OAuth | ⚠️ opcional |
| `AUTH0_CLIENT_ID` | Client ID de Auth0 | ⚠️ opcional |
| `AUTH0_CLIENT_SECRET` | Client Secret de Auth0 | ⚠️ opcional |

> ⚠️ Sin `CARBON_API_KEY`, el cálculo de huella de carbono usa valores locales estimados.  
> Sin las variables de Auth0, el login con Google no está disponible.

---

## API — Endpoints

La documentación interactiva completa está en `/docs` (Swagger UI) y `/redoc`.

### Autenticación

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `POST` | `/auth/login` | Login con usuario y contraseña | ❌ |
| `POST` | `/auth/register` | Registro de nueva cuenta | ❌ |
| `POST` | `/auth/login-google` | Login con Google (Auth0) | ❌ |
| `POST` | `/auth/forgot-password` | Solicitar código de recuperación | ❌ |
| `POST` | `/auth/reset-password` | Restablecer contraseña con código | ❌ |
| `POST` | `/auth/change-password` | Cambiar contraseña (usuario logueado) | ✅ |

### Contratos

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `GET` | `/contratos/mis-contratos` | Lista contratos del usuario | ✅ |

### Equipos

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `GET` | `/equipos/mis-equipos` | Lista equipos alquilados | ✅ |

### Tickets de soporte

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `GET` | `/tickets/mis-tickets` | Lista tickets del usuario | ✅ |
| `POST` | `/tickets/nuevo` | Crear un nuevo ticket | ✅ |

### Huella de carbono

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `GET` | `/carbono/mi-huella` | Calcula CO2 ahorrado del usuario | ✅ |

### Perfil

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `GET` | `/perfil/me` | Datos del usuario actual | ✅ |

### Sistema

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/health` | Estado de la API y la base de datos |
| `GET` | `/` | Info de la versión |

> **Autenticación**: todos los endpoints marcados con ✅ requieren header  
> `Authorization: Bearer <token>` obtenido al hacer login.

---

## Tests

### Requisitos

```bash
npm install
npx playwright install chromium
```

El backend debe estar corriendo en `http://localhost:8000` y el frontend en `http://localhost:5500`.

### Correr todos los tests

```bash
npm test
```

### Correr solo regresión

```bash
npx playwright test tests/actividad-3-regresion/
```

### Ver reporte HTML

```bash
npx playwright show-report
```

### Suite de tests incluida

| Actividad | Tipo | Tests |
|-----------|------|-------|
| actividad-1 | Login UI | `login.spec.js` |
| actividad-2 | API pura | `api.spec.js` |
| actividad-2 | Híbrida (API + UI) | `hibrida.spec.js` |
| actividad-2 | Mocking | `mocking.spec.js` |
| actividad-3 | **Regresión** | `regresion.spec.js` |

Los tests de regresión cubren:
- FC-01: Login (credenciales válidas, inválidas, campos vacíos)
- FC-02: Logout (limpieza de localStorage, redirección)
- FC-03: Registro (datos válidos, login del nuevo usuario)
- FC-04: Validaciones de formulario (contraseña corta, no coincide, campos vacíos)
- FC-05: Protección de rutas autenticadas (sin token, con token, token malformado)

---

## Estructura del proyecto

```
proyecto-green-computer/
├── backend/
│   ├── main.py               # App FastAPI, middlewares, rutas principales
│   ├── database.py           # Conexión MySQL y helpers query/execute
│   ├── requirements.txt      # Dependencias Python
│   ├── seed.py               # Script para poblar datos de prueba
│   ├── routers/
│   │   ├── auth.py           # Login, registro, OAuth, recuperación
│   │   ├── contratos.py      # Contratos de alquiler
│   │   ├── equipos.py        # Equipos alquilados
│   │   ├── tickets.py        # Tickets de soporte
│   │   ├── carbono.py        # Huella de carbono (Climatiq API)
│   │   └── perfil.py         # Perfil del usuario
│   └── utils/
│       ├── auth.py           # JWT helpers, hash, validación
│       └── auth0.py          # Integración Auth0 / Google OAuth
├── frontend/
│   ├── index.html            # Login y registro
│   ├── callback.html         # Callback OAuth de Auth0
│   ├── pages/
│   │   └── dashboard.html    # Dashboard principal del cliente
│   ├── js/
│   │   ├── login.js          # Lógica de login/registro
│   │   └── dashboard.js      # Lógica del dashboard
│   └── css/
│       └── ...               # Estilos del portal
├── tests/
│   ├── setup/                # Health check setup
│   ├── actividad-1/          # Tests E2E de login
│   ├── actividad-2/          # Tests API, mocking, híbridos
│   └── actividad-3-regresion/ # Suite de regresión completa
├── database_setup.sql        # Schema + datos de ejemplo
├── Dockerfile                # Imagen Docker del backend
├── docker-compose.yml        # Stack completo local (backend + MySQL)
├── railway.toml              # Configuración de despliegue en Railway
├── .env.example              # Plantilla de variables de entorno
├── .gitignore
├── package.json              # Dependencias Playwright
└── playwright.config.js      # Configuración de tests E2E
```
