const API = 'https://proyecto-green-computer-production.up.railway.app';

// ── AUTH0 ─────────────────────────────────────────────────
const auth0Config = {
  domain: "dev-syfyk7fe0keqki83.us.auth0.com",
  clientId: "zjQuX10YQZNO7pHt9GGYKiuKWFdGXHn9",
  authorizationParams: {
    redirect_uri: "http://localhost:5500/callback.html"
  }
};

let auth0Client = null;

async function initAuth0() {
  try {
    if (typeof auth0 !== 'undefined') {
      auth0Client = await auth0.createAuth0Client(auth0Config);
    }
  } catch(e) {
    console.warn('[AUTH0] No se pudo inicializar:', e.message);
  }
}

async function loginConGoogle() {
  if (!auth0Client) await initAuth0();
  await auth0Client.loginWithRedirect({
    authorizationParams: { connection: "google-oauth2" }
  });
}

// ← Ya no llamamos initAuth0() acá
// Se inicializa solo cuando el usuario hace click en el botón de Google

// ── HELPERS ───────────────────────────────────────────────
function show(viewId) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.getElementById(viewId).classList.add('active');
}

function togglePass(inputId, btn) {
  const inp = document.getElementById(inputId);
  inp.type = inp.type === 'password' ? 'text' : 'password';
  btn.textContent = inp.type === 'password' ? '👁' : '🙈';
}

function setLoading(btnId, loading, label) {
  const btn = document.getElementById(btnId);
  btn.disabled = loading;
  btn.innerHTML = loading ? '<span class="loading"></span>Procesando...' : label;
}

// ── LOGIN ─────────────────────────────────────────────────
async function doLogin() {
  const user = document.getElementById('login-user').value.trim();
  const pass = document.getElementById('login-pass').value;
  const err  = document.getElementById('login-error');
  err.classList.remove('show');

  if (!user || !pass) {
    err.textContent = 'Completá todos los campos.';
    err.classList.add('show');
    return;
  }

  setLoading('btn-login', true, 'Ingresar');
  try {
    const res = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: user, password: pass })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Credenciales inválidas');

    localStorage.clear();
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));

    await new Promise(resolve => setTimeout(resolve, 150));
    window.location.href = 'pages/dashboard.html';

  } catch(e) {
    err.textContent = e.message;
    err.classList.add('show');
  } finally {
    setLoading('btn-login', false, 'Ingresar');
  }
}

// ── REGISTRO ──────────────────────────────────────────────
async function doRegister() {
  const nombre    = document.getElementById('reg-nombre').value.trim();
  const apellido  = document.getElementById('reg-apellido').value.trim();
  const email     = document.getElementById('reg-email').value.trim();
  const telefono  = document.getElementById('reg-telefono').value.trim();
  const empresa   = document.getElementById('reg-empresa').value.trim();
  const username  = document.getElementById('reg-username').value.trim();
  const pass      = document.getElementById('reg-pass').value;
  const confirm   = document.getElementById('reg-confirm').value;
  const err       = document.getElementById('register-error');
  const ok        = document.getElementById('register-ok');

  err.classList.remove('show');
  ok.classList.remove('show');

  if (!nombre || !apellido || !email || !username || !pass || !confirm) {
    err.textContent = 'Completá todos los campos obligatorios (*).';
    err.classList.add('show');
    return;
  }
  if (!email.includes('@') || !email.includes('.')) {
    err.textContent = 'El email no es válido.';
    err.classList.add('show');
    return;
  }
  if (username.length < 3) {
    err.textContent = 'El nombre de usuario debe tener al menos 3 caracteres.';
    err.classList.add('show');
    return;
  }
  if (pass.length < 8) {
    err.textContent = 'La contraseña debe tener al menos 8 caracteres.';
    err.classList.add('show');
    return;
  }
  if (pass !== confirm) {
    err.textContent = 'Las contraseñas no coinciden.';
    err.classList.add('show');
    return;
  }

  setLoading('btn-register', true, 'Crear cuenta');
  try {
    const res = await fetch(`${API}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        nombre, apellido, email, username,
        password: pass,
        telefono: telefono || null,
        empresa:  empresa  || null,
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Error al crear la cuenta.');

    ok.textContent = `✅ ${data.message}`;
    ok.classList.add('show');

    ['reg-nombre','reg-apellido','reg-email','reg-telefono',
     'reg-empresa','reg-username','reg-pass','reg-confirm'].forEach(id => {
      document.getElementById(id).value = '';
    });

    setTimeout(() => show('view-login'), 2000);

  } catch(e) {
    err.textContent = e.message;
    err.classList.add('show');
  } finally {
    setLoading('btn-register', false, 'Crear cuenta');
  }
}

// ── FORGOT PASSWORD ───────────────────────────────────────
async function doForgot() {
  const email = document.getElementById('forgot-email').value.trim();
  const err = document.getElementById('forgot-error');
  const ok  = document.getElementById('forgot-ok');
  err.classList.remove('show');
  ok.classList.remove('show');

  if (!email) {
    err.textContent = 'Ingresá tu email.';
    err.classList.add('show');
    return;
  }

  setLoading('btn-forgot', true, 'Enviar código');
  try {
    const res = await fetch(`${API}/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Error al enviar');
    ok.textContent = 'Código enviado. Revisá tu bandeja de entrada.';
    ok.classList.add('show');
    setTimeout(() => show('view-reset'), 2000);
  } catch(e) {
    err.textContent = e.message;
    err.classList.add('show');
  } finally {
    setLoading('btn-forgot', false, 'Enviar código');
  }
}

// ── RESET PASSWORD ────────────────────────────────────────
async function doReset() {
  const code     = document.getElementById('reset-code').value.trim();
  const newPass  = document.getElementById('new-pass').value;
  const confPass = document.getElementById('confirm-pass').value;
  const err      = document.getElementById('reset-error');
  err.classList.remove('show');

  if (!code || !newPass || !confPass) {
    err.textContent = 'Completá todos los campos.';
    err.classList.add('show');
    return;
  }
  if (newPass !== confPass) {
    err.textContent = 'Las contraseñas no coinciden.';
    err.classList.add('show');
    return;
  }
  if (newPass.length < 8) {
    err.textContent = 'La contraseña debe tener al menos 8 caracteres.';
    err.classList.add('show');
    return;
  }

  setLoading('btn-reset', true, 'Cambiar contraseña');
  try {
    const res = await fetch(`${API}/auth/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code, new_password: newPass })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Error al cambiar');
    alert('✅ Contraseña actualizada. Ya podés ingresar.');
    show('view-login');
  } catch(e) {
    err.textContent = e.message;
    err.classList.add('show');
  } finally {
    setLoading('btn-reset', false, 'Cambiar contraseña');
  }
}

// ── STRENGTH BAR ──────────────────────────────────────────
function checkStrength(val) {
  const segs   = ['s1','s2','s3','s4'].map(id => document.getElementById(id));
  const colors = ['#ff5c6a','#ffaa00','#4daaff','#4dffa0'];
  const labels = ['Muy débil','Débil','Buena','Fuerte'];
  let score = 0;
  if (val.length >= 8)          score++;
  if (/[A-Z]/.test(val))        score++;
  if (/[0-9]/.test(val))        score++;
  if (/[^A-Za-z0-9]/.test(val)) score++;
  segs.forEach((s,i) => s.style.background = i < score ? colors[score-1] : 'rgba(255,255,255,0.08)');
  const lbl = document.getElementById('strength-label');
  if (lbl) lbl.textContent = val.length ? (labels[score-1] || '') : '';
}

// ── ENTER KEY ─────────────────────────────────────────────
document.addEventListener('keydown', e => {
  if (e.key !== 'Enter') return;
  if (document.getElementById('view-login').classList.contains('active'))         doLogin();
  else if (document.getElementById('view-register').classList.contains('active')) doRegister();
  else if (document.getElementById('view-forgot').classList.contains('active'))   doForgot();
  else if (document.getElementById('view-reset').classList.contains('active'))    doReset();
});
