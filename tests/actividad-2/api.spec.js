import { test, expect } from '@playwright/test';

const API_BASE = 'http://localhost:8000';

const CREDS_VALIDAS   = { username: 'prueba', password: 'Test1234!' };
const CREDS_INVALIDAS = { username: 'noexiste_xyz', password: 'mal123' };


async function obtenerToken(request) {
  const res = await request.post(`${API_BASE}/auth/login`, { data: CREDS_VALIDAS });
  expect(res.status()).toBe(200);
  const body = await res.json();
  return body.access_token;
}

test.describe('API Testing: Autenticación @api @smoke', () => {

  // TC-API-01: Login válido devuelve 200 y token JWT

  test('TC-API-01: POST /auth/login con credenciales válidas devuelve token JWT', async ({ request }) => {
    const response = await request.post(`${API_BASE}/auth/login`, {
      data: CREDS_VALIDAS
    });

    expect(response.status()).toBe(200);
    expect(response.ok()).toBeTruthy();

    const body = await response.json();
    expect(body).toHaveProperty('access_token');
    expect(body).toHaveProperty('token_type', 'bearer');
    expect(body.user).toHaveProperty('username', CREDS_VALIDAS.username);
  });

  // TC-API-02: Login inválido devuelve 401

  test('TC-API-02: POST /auth/login con credenciales inválidas devuelve 401', async ({ request }) => {
    const response = await request.post(`${API_BASE}/auth/login`, {
      data: CREDS_INVALIDAS
    });

    expect(response.status()).toBe(401);

    const body = await response.json();
    expect(body).toHaveProperty('detail');
  });

});


test.describe('API Testing: Registro @api @regression', () => {

  // TC-API-03: Registro de usuario nuevo exitoso

  test('TC-API-03: POST /auth/register con datos válidos crea la cuenta', async ({ request }) => {
    const ts = Date.now();
    const nuevoUsuario = {
      nombre:   'Test',
      apellido: 'Playwright',
      email:    `test_pw_${ts}@example.com`,
      username: `testpw_${ts}`,
      password: 'TestPass2024!',
    };

    const response = await request.post(`${API_BASE}/auth/register`, {
      data: nuevoUsuario
    });

    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body).toHaveProperty('username', nuevoUsuario.username);
  });

  // TC-API-04: Username duplicado devuelve error

  test('TC-API-04: POST /auth/register con username ya registrado devuelve error', async ({ request }) => {
    const response = await request.post(`${API_BASE}/auth/register`, {
      data: {
        nombre:   'Duplicado',
        apellido: 'Test',
        email:    `dup_${Date.now()}@example.com`,
        username: CREDS_VALIDAS.username,  // username que ya existe
        password: 'TestPass2024!',
      }
    });

    // El backend devuelve 400 o 409 para username duplicado
    expect([400, 409]).toContain(response.status());
  });

});


test.describe('API Testing: Infraestructura y rutas protegidas @api @smoke', () => {

  // TC-API-05: /health responde correctamente

  test('TC-API-05: GET /health devuelve estado healthy', async ({ request }) => {
    const response = await request.get(`${API_BASE}/health`);

    expect(response.status()).toBe(200);
  });

  // TC-API-06: Ruta protegida sin token → 401

  test('TC-API-06: GET /contratos/mis-contratos sin token devuelve 401', async ({ request }) => {
    const response = await request.get(`${API_BASE}/contratos/mis-contratos`);

    expect([401, 403]).toContain(response.status());
  });

  // TC-API-07: Ruta protegida con token válido → 200

  test('TC-API-07: GET /contratos/mis-contratos con token válido devuelve 200', async ({ request }) => {
    const token = await obtenerToken(request);

    const response = await request.get(`${API_BASE}/contratos/mis-contratos`, {
      headers: { Authorization: `Bearer ${token}` }
    });

    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(Array.isArray(body)).toBe(true);
  });

});
