import { test, expect } from '@playwright/test';

const USUARIO_VALIDO    = 'prueba';
const PASSWORD_VALIDA   = 'Test1234!';
const USUARIO_INVALIDO  = 'usuario_que_no_existe_xyz';
const PASSWORD_INVALIDA = 'claveIncorrecta999';

async function irAlLogin(page) {
  await page.goto('/');
  await expect(page.locator('#view-login')).toBeVisible();
}

async function completarLogin(page, usuario, contrasenia) {
  await page.locator('#login-user').fill(usuario);
  await page.locator('#login-pass').fill(contrasenia);
  await page.locator('#btn-login').click();
}

test.describe('Login – Green Computer Portal @smoke @critical', () => {

  // TC-01: Login válido con usuario existente

  test('TC-01: login exitoso redirige al dashboard @smoke', async ({ page }) => {
    await irAlLogin(page);

    // PASO 1: completar formulario con credenciales válidas
    await completarLogin(page, USUARIO_VALIDO, PASSWORD_VALIDA);

    // PASO 2: verificar redirección al dashboard
    await expect(page).toHaveURL(/dashboard\.html/, { timeout: 8000 });

    // PASO 3: verificar que el token JWT quedó en localStorage
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).not.toBeNull();
    // @ts-ignore
    expect(token.length).toBeGreaterThan(20);
  });

  // TC-02: Contraseña incorrecta
  
  test('TC-02: contraseña incorrecta muestra mensaje de error @regression', async ({ page }) => {
    await irAlLogin(page);

    // PASO 1: ingresar usuario válido con contraseña errónea
    await completarLogin(page, USUARIO_VALIDO, PASSWORD_INVALIDA);

    // PASO 2: verificar que aparece el mensaje de error
    const errorMsg = page.locator('#login-error');
    await expect(errorMsg).toBeVisible();
    await expect(errorMsg).toContainText(/credenciales|contraseña|usuario|inválid/i);

    // PASO 3: verificar que NO redirigió
    await expect(page).not.toHaveURL(/dashboard/);
  });

  // TC-03: Usuario inexistente
 
  test('TC-03: usuario inexistente muestra error de credenciales @regression', async ({ page }) => {
    await irAlLogin(page);

    await completarLogin(page, USUARIO_INVALIDO, PASSWORD_INVALIDA);

    const errorMsg = page.locator('#login-error');
    await expect(errorMsg).toBeVisible();
    await expect(errorMsg).toContainText(/credenciales|contraseña|usuario|inválid/i);
  });

  // TC-04: Campos vacíos
  
  test('TC-04: campos vacíos muestran validación sin llamar al API @regression', async ({ page }) => {
    await irAlLogin(page);

    // PASO 1: click en Ingresar sin completar nada
    await page.locator('#btn-login').click();

    // PASO 2: verificar mensaje de validación del frontend
    const errorMsg = page.locator('#login-error');
    await expect(errorMsg).toBeVisible();
    await expect(errorMsg).toContainText(/complet/i);
  });

  // TC-05: Toggle de contraseña (mostrar/ocultar)

  test('TC-05: botón ojo alterna la visibilidad de la contraseña @regression', async ({ page }) => {
    await irAlLogin(page);

    const passInput = page.locator('#login-pass');
    const toggleBtn = page.locator('#view-login .toggle-pass').first();

    // PASO 1: estado inicial debe ser password oculta
    await expect(passInput).toHaveAttribute('type', 'password');

    // PASO 2: click muestra la contraseña
    await toggleBtn.click();
    await expect(passInput).toHaveAttribute('type', 'text');

    // PASO 3: segundo click vuelve a ocultarla
    await toggleBtn.click();
    await expect(passInput).toHaveAttribute('type', 'password');
  });

  // TC-06: Enlace "Crear cuenta nueva"

  test('TC-06: enlace "Crear cuenta nueva" muestra el formulario de registro @regression', async ({ page }) => {
    await irAlLogin(page);

    await page.locator('a', { hasText: 'Crear cuenta nueva' }).click();

    await expect(page.locator('#view-register')).toBeVisible();
    await expect(page.locator('#view-login')).not.toBeVisible();
  });

  // TC-07: Enlace "¿Olvidaste tu contraseña?"

  test('TC-07: enlace de recuperación muestra la vista de forgot password @regression', async ({ page }) => {
    await irAlLogin(page);

    await page.locator('a', { hasText: /olvidaste/i }).click();

    await expect(page.locator('#view-forgot')).toBeVisible();
    await expect(page.locator('#view-login')).not.toBeVisible();
  });

});
