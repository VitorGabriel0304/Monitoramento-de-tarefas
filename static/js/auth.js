const API = '/api';

// Tabs
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
  });
});

// Login
document.getElementById('btn-login').addEventListener('click', async () => {
  const email    = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;
  const errEl    = document.getElementById('login-error');
  errEl.classList.add('hidden');

  if (!email || !password) { show(errEl, 'Preencha e-mail e senha.'); return; }

  try {
    const res  = await fetch(`${API}/users/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (!res.ok) { show(errEl, data.error); return; }
    localStorage.setItem('user', JSON.stringify(data.user));
    window.location.href = '/dashboard';
  } catch {
    show(errEl, 'Não foi possível conectar ao servidor.');
  }
});

// Register
document.getElementById('btn-register').addEventListener('click', async () => {
  const name     = document.getElementById('reg-name').value.trim();
  const email    = document.getElementById('reg-email').value.trim();
  const password = document.getElementById('reg-password').value;
  const errEl    = document.getElementById('reg-error');
  const okEl     = document.getElementById('reg-success');
  errEl.classList.add('hidden');
  okEl.classList.add('hidden');

  if (!name || !email || !password) { show(errEl, 'Preencha todos os campos.'); return; }
  if (password.length < 6) { show(errEl, 'A senha deve ter pelo menos 6 caracteres.'); return; }

  try {
    const res  = await fetch(`${API}/users/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password })
    });
    const data = await res.json();
    if (!res.ok) { show(errEl, data.error); return; }
    show(okEl, 'Conta criada com sucesso! Faça login.');
    document.getElementById('reg-name').value = '';
    document.getElementById('reg-email').value = '';
    document.getElementById('reg-password').value = '';
  } catch {
    show(errEl, 'Não foi possível conectar ao servidor.');
  }
});

function show(el, msg) {
  el.textContent = msg;
  el.classList.remove('hidden');
}