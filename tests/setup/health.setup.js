import { test, expect } from '@playwright/test';

const API_BASE = 'http://localhost:8000';

test('verificar que el backend de Green Computer está activo', async ({ request }) => {
  console.log('🔍 [SETUP] Verificando disponibilidad del backend...');

  const response = await request.get(`${API_BASE}/health`);

  expect(
    response.status(),
    `❌ El backend no responde en ${API_BASE}/health. ` +
    `Iniciá el servidor con: cd backend && uvicorn main:app --reload --port 8000`
  ).toBe(200);

  console.log('✅ [SETUP] Backend disponible');
});

