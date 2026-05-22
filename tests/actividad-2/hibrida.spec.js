import { test, expect } from '@playwright/test';

const API_BASE = 'http://localhost:8000';

async function crearUsuarioViaAPI(request) {
  const ts = Date.now();
  const datos = {
    nombre:   'PW',
    apellido: 'Hibrido',
    email:    `pw_hibrido_${ts}@example.com`,
    username: `pw_h_${ts}`,
    password: 'Hibrido2024!',
  };

  const res = await request.post(`${API_BASE}/auth/register`, { data: datos });
  expect(res.status()).toBe(200);

  return datos;
}

test.describe('Patrón: API Setup + UI Test @hibrida @e2e', () => {

  // TC-HYB-01: Crear usuario por API → verificar login en UI

  test('TC-HYB-01: usuario creado por API puede iniciar sesión en la UI', async ({ page, request }) => {
    // ── PASO 1: preparar estado vía API
    const creds = await crearUsuarioViaAPI(request);

    // ── PASO 2: validar desde la UI
    await page.goto('/');
    await page.locator('#login-user').fill(creds.username);
    await page.locator('#login-pass').fill(creds.password);
    await page.locator('#btn-login').click();

    // ── PASO 3: verificar redirección exitosa
    await expect(page).toHaveURL(/dashboard\.html/, { timeout: 8000 });

    // ── PASO 4: verificar token en localStorage
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeTruthy();
  });

  // TC-HYB-02: Usuario real → falla con contraseña incorrecta en UI

  test('TC-HYB-02: usuario creado por API falla login con contraseña incorrecta en UI', async ({ page, request }) => {
    // ── PASO 1: crear usuario real vía API
    const creds = await crearUsuarioViaAPI(request);

    // ── PASO 2: intentar login con contraseña incorrecta
    await page.goto('/');
    await page.locator('#login-user').fill(creds.username);
    await page.locator('#login-pass').fill('claveIncorrecta999');
    await page.locator('#btn-login').click();

    // ── PASO 3: verificar error visible y sin redirección
    await expect(page.locator('#login-error')).toBeVisible({ timeout: 8000 });
    await expect(page).not.toHaveURL(/dashboard/);
  });

  // TC-HYB-03: Datos creados por API coinciden con lo visible en la UI

  test('TC-HYB-03: datos del usuario registrado por API se ven en la UI', async ({ page, request }) => {
    // ── PASO 1: crear usuario con datos conocidos
    const ts = Date.now();
    const datos = {
      nombre:   'Carlos',
      apellido: 'Verificado',
      email:    `carlos_v_${ts}@example.com`,
      username: `carlos_${ts}`,
      password: 'Verificado2024!',
    };
    const regRes = await request.post(`${API_BASE}/auth/register`, { data: datos });
    expect(regRes.status()).toBe(200);

    // ── PASO 2: login en UI y verificar que llega al dashboard
    await page.goto('/');
    await page.locator('#login-user').fill(datos.username);
    await page.locator('#login-pass').fill(datos.password);
    await page.locator('#btn-login').click();

    await page.waitForURL(/dashboard/, { timeout: 8000 });

    // ── PASO 3: verificar que el nombre del usuario aparece en el dashboard
    const userJson = await page.evaluate(() => localStorage.getItem('user'));
    const userData = JSON.parse(userJson);
    expect(userData.username).toBe(datos.username);
  });

  // TC-HYB-04: API sana + login UI funcionan de forma coherente

  test('TC-HYB-04: cuando /health es OK el login en UI también funciona', async ({ page, request }) => {
    // ── PASO 1: verificar por API que el backend está disponible
    const healthRes = await request.get(`${API_BASE}/health`);
    expect(healthRes.status()).toBe(200);

    // ── PASO 2: si el backend está sano, el login en UI debe funcionar
    await page.goto('/');
    await page.locator('#login-user').fill('prueba');
    await page.locator('#login-pass').fill('Test1234!');
    await page.locator('#btn-login').click();

    await expect(page).toHaveURL(/dashboard\.html/, { timeout: 8000 });
  });

});


