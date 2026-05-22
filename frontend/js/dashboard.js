const API = 'http://localhost:8000';

let token = null;
let currentUser = {};
let ticketType = 'consulta';

function getToken() {
  const t = localStorage.getItem('token');
  if (!t || t === 'null' || t === 'undefined') {
    return null;
  }
  return t;
}

window.addEventListener('DOMContentLoaded', async () => {
  console.log('🚀 Dashboard cargando...');
  
  token = getToken();
  
  if (!token) {
    console.error('❌ No hay token válido, redirigiendo a login...');
    window.location.href = '../index.html';
    return;
  }

  console.log('✅ Token encontrado:', token.substring(0, 30) + '...');

  try {
    const userStr = localStorage.getItem('user');
    if (userStr && userStr !== 'null' && userStr !== 'undefined') {
      currentUser = JSON.parse(userStr);
      console.log('✅ Usuario cargado:', currentUser.nombre);
    } else {
      console.warn('⚠️ No hay datos de usuario en localStorage');
      currentUser = {};
    }
  } catch(e) {
    console.error('❌ Error parseando usuario:', e);
    currentUser = {};
  }

  const nombreInicial = (currentUser.nombre || 'U')[0].toUpperCase();
  document.getElementById('ua').textContent = nombreInicial;
  document.getElementById('un').textContent = currentUser.nombre || 'Usuario';

  console.log('📊 Cargando datos del dashboard...');
  
  await loadAll();
  
  console.log('✅ Dashboard cargado completamente');
});

async function authFetch(url, opts = {}) {
  const currentToken = getToken();
  
  if (!currentToken) {
    console.error('❌ Token inválido en authFetch, cerrando sesión...');
    logout();
    return null;
  }

  opts.headers = { 
    ...opts.headers, 
    'Authorization': `Bearer ${currentToken}`, 
    'Content-Type': 'application/json' 
  };

  try {
    console.log('🔄 Fetching:', url);
    const res = await fetch(API + url, opts);
    
    if (res.status === 401) {
      console.error('❌ 401 Unauthorized en:', url);
      logout();
      return null;
    }

    if (!res.ok) {
      console.warn('⚠️ Response no OK:', res.status, url);
    }
    
    return res;
  } catch(error) {
    console.error('❌ Error en authFetch:', url, error);
    return null;
  }
}

async function loadAll() {
  console.log('📥 Iniciando carga de todos los datos...');
  try {
    await Promise.all([
      loadContratos(), 
      loadTickets(), 
      loadEquipos(), 
      loadCO2()
    ]);
    console.log('✅ Todos los datos cargados');
  } catch(error) {
    console.error('❌ Error en loadAll:', error);
  }
}

async function loadContratos() {
  try {
    console.log('📄 Cargando contratos...');
    const res  = await authFetch('/contratos/mis-contratos');
    if (!res) return;
    const data = await res.json();
    
    document.getElementById('kpi-vigentes').textContent   = data.filter(c => c.estado === 'vigente').length;
    document.getElementById('kpi-pendientes').textContent = data.filter(c => c.estado === 'pendiente').length;
    document.getElementById('kpi-terminados').textContent = data.filter(c => c.estado === 'terminado').length;
    document.getElementById('kpi-total').textContent      = data.length;
    
    document.getElementById('tbody-contratos').innerHTML  = data.map(c => {
      const hoy       = new Date();
      const vencim    = c.fecha_fin ? new Date(c.fecha_fin) : null;
      const diasRest  = vencim ? Math.ceil((vencim - hoy) / (1000*60*60*24)) : null;
      const alertaVenc = diasRest !== null && diasRest >= 0 && diasRest <= 30 && c.estado === 'vigente'
        ? `<span title="Vence en ${diasRest} días" style="color:var(--warn);font-size:12px;margin-left:6px">⚠️ ${diasRest}d</span>`
        : '';

      const leasingBar = c.tipo_contrato === 'leasing' && c.cuotas_total
        ? `<div style="margin-top:6px">
             <div style="font-size:11px;color:var(--muted);margin-bottom:3px">
               Leasing: ${c.cuotas_pagadas}/${c.cuotas_total} cuotas
             </div>
             <div style="background:rgba(255,255,255,0.08);border-radius:4px;height:5px;width:100%">
               <div style="background:var(--accent);height:5px;border-radius:4px;width:${Math.round((c.cuotas_pagadas/c.cuotas_total)*100)}%"></div>
             </div>
           </div>`
        : '';

      return `
        <tr>
          <td>#${c.id}</td>
          <td>${c.equipo_nombre}${leasingBar}</td>
          <td>${formatDate(c.fecha_inicio)}</td>
          <td>${formatDate(c.fecha_fin)}${alertaVenc}</td>
          <td>$${Number(c.valor_mensual).toLocaleString('es-AR')}/mes</td>
          <td><span class="badge badge-${c.estado === 'vigente' ? 'active' : c.estado === 'pendiente' ? 'pending' : 'done'}">${capitalize(c.estado)}</span></td>
        </tr>`;
    }).join('') || '<tr><td colspan="6" style="color:var(--muted);text-align:center;padding:24px">No hay contratos</td></tr>';
    
    console.log('✅ Contratos cargados:', data.length);
  } catch(e) { 
    console.error('❌ Error cargando contratos:', e); 
  }
}

async function loadTickets() {
  try {
    console.log('🎫 Cargando tickets...');
    const [resT, resE] = await Promise.all([
      authFetch('/tickets/mis-tickets'),
      authFetch('/equipos/mis-equipos')
    ]);
    
    if (!resT || !resE) return;
    
    const tickets = await resT.json();
    const equipos = await resE.json();

    document.getElementById('tf-equipo').innerHTML =
      '<option value="">Seleccioná un equipo</option>' +
      equipos.map(e => `<option value="${e.id}">${e.nombre} – ${e.modelo}</option>`).join('');

    document.getElementById('tbody-tickets').innerHTML = tickets.map(t => `
      <tr>
        <td>#${t.id}</td>
        <td><span class="badge badge-${t.tipo === 'consulta' ? 'pending' : 'active'}">${t.tipo === 'consulta' ? '💬 Consulta' : '🛡️ Garantía'}</span></td>
        <td>${t.equipo_nombre || '-'}</td>
        <td>${t.asunto}</td>
        <td>${formatDate(t.fecha_creacion)}</td>
        <td><span class="badge badge-${t.estado === 'abierto' ? 'pending' : t.estado === 'cerrado' ? 'done' : 'active'}">${capitalize(t.estado)}</span></td>
        <td style="display:flex;gap:6px">
          ${t.estado === 'abierto'
            ? `<button class="btn btn-sm" style="padding:5px 10px;font-size:12px" onclick="openEditTicket(${t.id},'${escHtml(t.asunto)}','${escHtml(t.detalle)}','${t.tipo}')">✏️</button>`
            : '<span style="color:var(--muted);font-size:12px">—</span>'}
          ${t.estado !== 'en_proceso'
            ? `<button class="btn btn-sm" style="padding:5px 10px;font-size:12px;background:rgba(255,92,106,0.15);color:var(--error);border:1px solid rgba(255,92,106,0.3)" onclick="deleteTicket(${t.id})">🗑️</button>`
            : ''}
        </td>
      </tr>`).join('') || '<tr><td colspan="7" style="color:var(--muted);text-align:center;padding:24px">No tenés tickets aún</td></tr>';
    
    console.log('✅ Tickets cargados:', tickets.length);
  } catch(e) { 
    console.error('❌ Error cargando tickets:', e); 
  }
}

function openTicketForm(tipo) {
  ticketType = tipo;
  document.getElementById('tf-title').textContent = tipo === 'consulta' ? '💬 Nuevo Ticket de Consulta' : '🛡️ Ticket de Garantía';
  document.getElementById('ticket-form').classList.add('show');
  document.getElementById('ticket-form').scrollIntoView({ behavior: 'smooth' });
}

function closeTicketForm() { 
  document.getElementById('ticket-form').classList.remove('show'); 
}

async function submitTicket() {
  const equipo  = document.getElementById('tf-equipo').value;
  const asunto  = document.getElementById('tf-asunto').value.trim();
  const detalle = document.getElementById('tf-detalle').value.trim();
  
  if (!asunto || !detalle) { 
    alert('Completá asunto y detalle.'); 
    return; 
  }
  
  try {
    const res  = await authFetch('/tickets/crear', { 
      method: 'POST', 
      body: JSON.stringify({ 
        tipo: ticketType, 
        equipo_id: equipo || null, 
        asunto, 
        detalle 
      }) 
    });
    
    if (!res) return;
    const data = await res.json();
    
    const ok   = document.getElementById('tf-ok');
    ok.textContent = '✅ Ticket enviado correctamente. N°' + data.id;
    ok.classList.add('show');
    
    document.getElementById('tf-asunto').value  = '';
    document.getElementById('tf-detalle').value = '';
    
    await loadTickets();
    
    setTimeout(() => { 
      ok.classList.remove('show'); 
      closeTicketForm(); 
    }, 3000);
  } catch(e) { 
    console.error('Error al enviar ticket:', e);
    alert('Error al enviar el ticket.'); 
  }
}

function openEditTicket(id, asunto, detalle, tipo) {
  document.getElementById('edit-ticket-id').value = id;
  document.getElementById('edit-asunto').value    = asunto;
  document.getElementById('edit-detalle').value   = detalle;
  document.getElementById('edit-ticket-subtitle').textContent = `Ticket #${id} · ${tipo === 'consulta' ? '💬 Consulta' : '🛡️ Garantía'}`;
  document.getElementById('edit-ok').classList.remove('show');
  document.getElementById('edit-err').classList.remove('show');
  document.getElementById('modal-edit-ticket').classList.add('show');
}

function closeEditTicket() { 
  document.getElementById('modal-edit-ticket').classList.remove('show'); 
}

async function saveEditTicket() {
  const id      = document.getElementById('edit-ticket-id').value;
  const asunto  = document.getElementById('edit-asunto').value.trim();
  const detalle = document.getElementById('edit-detalle').value.trim();
  const ok  = document.getElementById('edit-ok');
  const err = document.getElementById('edit-err');
  
  ok.classList.remove('show'); 
  err.classList.remove('show');
  
  if (!asunto || !detalle) { 
    err.textContent = 'Completá todos los campos.'; 
    err.classList.add('show'); 
    return; 
  }
  
  try {
    const res  = await authFetch(`/tickets/${id}`, { 
      method: 'PUT', 
      body: JSON.stringify({ asunto, detalle }) 
    });
    
    if (!res) return;
    const data = await res.json();
    
    if (!res.ok) throw new Error(data.detail || 'Error al guardar.');
    
    ok.textContent = '✅ Ticket actualizado correctamente.';
    ok.classList.add('show');
    
    await loadTickets();
    
    setTimeout(() => closeEditTicket(), 1500);
  } catch(e) { 
    err.textContent = e.message; 
    err.classList.add('show'); 
  }
}

async function deleteTicket(id) {
  if (!confirm(`¿Seguro que querés eliminar el Ticket #${id}? Esta acción no se puede deshacer.`)) return;
  
  try {
    const res  = await authFetch(`/tickets/${id}`, { method: 'DELETE' });
    if (!res) return;
    
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Error al eliminar.');
    
    await loadTickets();
  } catch(e) { 
    alert(e.message); 
  }
}

async function loadCO2() {
  try {
    console.log('🌱 Cargando huella de CO2...');
    const res   = await authFetch('/carbono/mi-huella');
    if (!res) return;
    
    const data  = await res.json();
    const total = data.total_kg_co2;
    
    document.getElementById('co2-total').textContent   = total.toFixed(1);
    document.getElementById('co2-badge').textContent   = `${total.toFixed(1)} kg`;
    document.getElementById('co2-km').textContent      = (total * 6.3).toFixed(0);
    document.getElementById('co2-trees').textContent   = (total / 21.77).toFixed(1);
    document.getElementById('co2-kwh').textContent     = (total * 1.22).toFixed(0);
    document.getElementById('co2-devices').textContent = data.equipos?.length || '-';
    
    document.getElementById('tbody-co2').innerHTML = (data.equipos || []).map(e => `
      <tr>
        <td>${e.nombre}</td>
        <td>${e.dias_alquilado} días</td>
        <td><strong style="color:var(--accent)">${e.kg_co2.toFixed(2)}</strong></td>
        <td>≈ ${(e.kg_co2 * 6.3).toFixed(0)} km en auto</td>
      </tr>`).join('');
    
    console.log('✅ CO2 cargado:', total.toFixed(1), 'kg');
  } catch(e) { 
    document.getElementById('co2-total').textContent = 'N/D'; 
    console.error('❌ Error cargando CO2:', e); 
  }
}

async function loadEquipos() {
  try {
    console.log('💻 Cargando equipos...');
    const res  = await authFetch('/equipos/mis-equipos');
    if (!res) return;
    
    const data = await res.json();
    
    document.getElementById('equip-grid').innerHTML = data.map(e => `
      <div class="equip-card">
        <div class="equip-header">
          <div class="equip-icon">${e.tipo === 'notebook' ? '💻' : '🖥️'}</div>
          <span class="badge badge-active">Activo</span>
        </div>
        <div class="equip-name">${e.nombre}</div>
        <div class="equip-model">${e.modelo}</div>
        <div class="equip-specs">
          ${e.specs?.split(',').map(s => `<span class="spec-tag">${s.trim()}</span>`).join('') || ''}
        </div>
        <div class="equip-footer">
          <button class="btn btn-sm" onclick="showManual(${e.id})">📖 Manual</button>
        </div>
      </div>`).join('') || '<div style="color:var(--muted)">No tenés equipos alquilados activos.</div>';
    
    console.log('✅ Equipos cargados:', data.length);
  } catch(e) { 
    console.error('❌ Error cargando equipos:', e); 
  }
}

async function showManual(equipoId) {
  try {
    const res = await authFetch(`/equipos/${equipoId}/manual`);
    if (!res) return;
    
    const d   = await res.json();
    
    document.getElementById('modal-title').textContent  = d.nombre;
    document.getElementById('modal-model').textContent  = d.modelo;
    document.getElementById('modal-content').innerHTML  = d.manual_html || '<p>Manual no disponible.</p>';
    document.getElementById('modal-manual').classList.add('show');
  } catch(e) { 
    alert('Error al cargar el manual.'); 
  }
}

function closeModal() { 
  document.getElementById('modal-manual').classList.remove('show'); 
}

async function loadPerfil() {
  try {
    const res = await authFetch('/perfil/');
    if (!res) return;
    
    const d   = await res.json();
    
    document.getElementById('pf-nombre').value = d.nombre || '';
    document.getElementById('pf-email').value  = d.email  || '';
    
    const nombreCompleto = d.apellido ? `${d.nombre} ${d.apellido}` : d.nombre;
    document.getElementById('perfil-nombre-display').textContent = nombreCompleto || '-';
    document.getElementById('perfil-email-display').textContent  = d.email  || '-';
    document.getElementById('perfil-desde').textContent    = 'Cliente desde ' + formatDate(d.created_at);
    document.getElementById('perfil-avatar').textContent   = (d.nombre || 'U')[0].toUpperCase();
  } catch(e) { 
    console.error('Error cargando perfil:', e); 
  }
}

async function updatePerfil() {
  const nombre = document.getElementById('pf-nombre').value.trim();
  const email  = document.getElementById('pf-email').value.trim();
  const ok  = document.getElementById('perfil-ok');
  const err = document.getElementById('perfil-err');
  
  ok.classList.remove('show'); 
  err.classList.remove('show');
  
  if (!nombre && !email) { 
    err.textContent = 'Completá al menos un campo.'; 
    err.classList.add('show'); 
    return; 
  }
  
  try {
    const res  = await authFetch('/perfil/', { 
      method: 'PUT', 
      body: JSON.stringify({ nombre: nombre || null, email: email || null }) 
    });
    
    if (!res) return;
    const data = await res.json();
    
    if (!res.ok) throw new Error(data.detail || 'Error al guardar.');
    
    ok.textContent = '✅ Perfil actualizado correctamente.';
    ok.classList.add('show');
    
    document.getElementById('un').textContent                    = nombre || currentUser.nombre;
    document.getElementById('ua').textContent                    = (nombre || currentUser.nombre || 'U')[0].toUpperCase();
    document.getElementById('perfil-nombre-display').textContent = nombre;
    document.getElementById('perfil-email-display').textContent  = email;
    document.getElementById('perfil-avatar').textContent         = (nombre || 'U')[0].toUpperCase();
  } catch(e) { 
    err.textContent = e.message; 
    err.classList.add('show'); 
  }
}

async function changePassword() {
  const curr = document.getElementById('cp-current').value;
  const newP = document.getElementById('cp-new').value;
  const conf = document.getElementById('cp-confirm').value;
  const ok   = document.getElementById('pass-ok');
  const err  = document.getElementById('pass-err');
  
  ok.classList.remove('show'); 
  err.classList.remove('show');
  
  if (newP !== conf)   { 
    err.textContent = 'Las contraseñas no coinciden.'; 
    err.classList.add('show'); 
    return; 
  }
  
  if (newP.length < 8) { 
    err.textContent = 'Mínimo 8 caracteres.';          
    err.classList.add('show'); 
    return; 
  }
  
  try {
    const res  = await authFetch('/perfil/cambiar-password', { 
      method: 'PUT', 
      body: JSON.stringify({ current_password: curr, new_password: newP }) 
    });
    
    if (!res) return;
    const data = await res.json();
    
    if (!res.ok) throw new Error(data.detail || 'Error');
    
    ok.textContent = '✅ Contraseña actualizada.';
    ok.classList.add('show');
    
    document.getElementById('cp-current').value = '';
    document.getElementById('cp-new').value     = '';
    document.getElementById('cp-confirm').value = '';
  } catch(e) { 
    err.textContent = e.message; 
    err.classList.add('show'); 
  }
}

async function desactivarCuenta() {
  if (!confirm('⚠️ ¿Seguro que querés desactivar tu cuenta? Perderás acceso al portal.\n\nPodés reactivarla contactando a soporte.')) return;
  
  try {
    const res  = await authFetch('/perfil/', { method: 'DELETE' });
    if (!res) return;
    
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Error');
    
    alert('Tu cuenta fue desactivada. Serás redirigido al login.');
    logout();
  } catch(e) { 
    alert(e.message); 
  }
}

function showSection(id) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  event.currentTarget.classList.add('active');
  
  const titles = { 
    'sec-contratos':'Mis Contratos', 
    'sec-tickets':'Tickets', 
    'sec-co2':'Huella de CO₂', 
    'sec-equipos':'Mis Equipos', 
    'sec-perfil':'Mi Perfil' 
  };
  
  const subs = { 
    'sec-contratos':'Historial completo de alquileres', 
    'sec-tickets':'Consultas y garantías', 
    'sec-co2':'Tu impacto ambiental', 
    'sec-equipos':'Equipos alquilados activos', 
    'sec-perfil':'Datos personales y seguridad' 
  };
  
  document.getElementById('page-title').textContent = titles[id];
  document.getElementById('page-sub').textContent   = subs[id];
  
  if (id === 'sec-perfil') loadPerfil();
}

function logout() { 
  console.log('🚪 Cerrando sesión...');
  localStorage.clear(); 
  window.location.href = '../index.html'; 
}

function formatDate(d) { 
  if (!d) return '-'; 
  return new Date(d).toLocaleDateString('es-AR'); 
}

function capitalize(s) { 
  return s ? s[0].toUpperCase() + s.slice(1) : ''; 
}

function escHtml(s) { 
  return (s || '').replace(/'/g, "\\'").replace(/"/g, '&quot;'); 
}
