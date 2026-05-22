import { test, expect } from '@playwright/test';

const API_LOGIN      = '**/auth/login';
const API_CONTRATOS  = '**/contratos/mis-contratos';

async function mockLoginExitoso(page, token = 'fake.jwt.token.para.prueba') {
  await page.route(API_LOGIN, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        access_token: token,
        token_type:   'bearer',
        user: { id: 99, nombre: 'Usuario Mock', email: 'mock@example.com', username: 'mockuser' }
      })
    });
  });
}

async function hacerLoginEnUI(page) {
  await page.goto('/');
  await page.locator('#login-user').fill('cualquierUsuario');
  await page.locator('#login-pass').fill('cualquierClave1!');
  await page.locator('#btn-login').click();
}

test.describe('Mocking: Simular estados de error @mock @regression', () => {

  // TC-MOCK-01: Error 500 en login → UI muestra error, no redirige

  test('TC-MOCK-01: error 500 del servidor en login muestra mensaje en UI', async ({ page }) => {
    // SETUP: interceptar **/auth/login y devolver HTTP 500
    await page.route(API_LOGIN, async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal Server Error' })
      });
    });

    await page.goto('/');
    await page.locator('#login-user').fill('prueba');
    await page.locator('#login-pass').fill('Test1234!');
    await page.locator('#btn-login').click();

    // VERIFICACIÓN: la UI debe mostrar error, no redirigir
    await expect(page.locator('#login-error')).toBeVisible({ timeout: 5000 });
    await expect(page).not.toHaveURL(/dashboard/);
  });

  // TC-MOCK-02: Respuesta exitosa falsa → redirige al dashboard

  test('TC-MOCK-02: respuesta mockeada exitosa de login redirige al dashboard', async ({ page }) => {
    // SETUP: simular respuesta válida sin backend real
    await mockLoginExitoso(page);

    await hacerLoginEnUI(page);

    // VERIFICACIÓN: debe redirigir como si fuera un login real
    await expect(page).toHaveURL(/dashboard\.html/, { timeout: 6000 });
  });

});


test.describe('Mocking: Simular datos específicos @mock @regression', () => {

  // TC-MOCK-03: Lista vacía de contratos → UI muestra estado vacío

  test('TC-MOCK-03: lista de contratos vacía no muestra filas en la tabla', async ({ page }) => {
    // SETUP: login mockeado + contratos vacíos
    await mockLoginExitoso(page);

    await page.route(API_CONTRATOS, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      });
    });

    await hacerLoginEnUI(page);
    await page.waitForURL(/dashboard/, { timeout: 6000 });

    // VERIFICACIÓN: no debe haber filas de datos
    const filas = page.locator('#tabla-contratos tbody tr, .contrato-item');
    await expect(filas).toHaveCount(0, { timeout: 5000 });
  });

  // TC-MOCK-04: Error 401 en contratos → redirige al login

  test('TC-MOCK-04: respuesta 401 en datos protegidos redirige al login', async ({ page }) => {
    // SETUP: login exitoso pero /contratos devuelve 401
    await mockLoginExitoso(page);

    await page.route(API_CONTRATOS, async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Could not validate credentials' })
      });
    });

    await hacerLoginEnUI(page);
    await page.waitForURL(/dashboard/, { timeout: 6000 });

    // VERIFICACIÓN: el dashboard debe detectar el 401 y redirigir
    await expect(page).toHaveURL(/index\.html/, { timeout: 8000 });
  });

// TC-MOCK-05: El token mockeado queda en localStorage para ser enviado

  test('TC-MOCK-05: el token mockeado queda en localStorage listo para enviarse', async ({ page }) => {
    const TOKEN_ESPERADO = 'mi_token_de_prueba_123';

    // SETUP: login con token conocido
    await mockLoginExitoso(page, TOKEN_ESPERADO);
    await hacerLoginEnUI(page);
    await page.waitForURL(/dashboard/, { timeout: 6000 });


    // VERIFICACIÓN: el token debe estar en localStorage
    const tokenGuardado = await page.evaluate(() => localStorage.getItem('token'));
    expect(tokenGuardado).toBe(TOKEN_ESPERADO);

    // VERIFICACIÓN: el objeto user también fue guardado correctamente
    const userGuardado = await page.evaluate(() => localStorage.getItem('user'));
    const user = JSON.parse(userGuardado);
    expect(user).toHaveProperty('username', 'mockuser');
  });

});

