// ─── Configuração da API ─────────────────────────────────────────
const API = window.location.hostname.includes('localhost')
  ? 'http://localhost:5000/api'
  : 'https://minhastafefas.up.railway.app/api';

// ─── Elementos ──────────────────────────────────────────────────
const btnLogin = document.getElementById('btn-login');
const btnRegister = document.getElementById('btn-register');

const loginError = document.getElementById('login-error');
const registerError = document.getElementById('reg-error');

// ─── LOGIN ──────────────────────────────────────────────────────
if (btnLogin) {
  btnLogin.addEventListener('click', async () => {

    loginError.classList.add('hidden');

    const payload = {
      email: document.getElementById('login-email').value.trim(),
      password: document.getElementById('login-password').value.trim()
    };

    try {
      const res = await fetch(`${API}/users/login`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error();

      const data = await res.json();
      localStorage.setItem('user', JSON.stringify(data));

      window.location.href = '/dashboard';

    } catch {
      loginError.textContent = 'Erro ao fazer login.';
      loginError.classList.remove('hidden');
    }
  });
}

// ─── REGISTRO ───────────────────────────────────────────────────
if (btnRegister) {
  btnRegister.addEventListener('click', async () => {

    registerError.classList.add('hidden');

    const payload = {
      name: document.getElementById('reg-name').value.trim(),
      email: document.getElementById('reg-email').value.trim(),
      password: document.getElementById('reg-password').value.trim()
    };

    try {
      const res = await fetch(`${API}/users/register`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error();

      const data = await res.json();
      localStorage.setItem('user', JSON.stringify(data));

      window.location.href = '/dashboard';

    } catch {
      registerError.textContent = 'Erro ao criar conta.';
      registerError.classList.remove('hidden');
    }
  });
}


// ─── Troca de abas ─────────────────────────────────────────────
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));

    btn.classList.add('active');
    document.getElementById(`tab-${btn.dataset.tab}`).classList.add('active');
  });
});