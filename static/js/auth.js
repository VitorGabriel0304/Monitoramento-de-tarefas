// ─── Configuração da API ─────────────────────────────────────────
const API = window.location.hostname.includes('localhost')
  ? 'http://localhost:5000/api'
  : 'https://minhastafefas.up.railway.app/api';

// ─── Formulários ─────────────────────────────────────────────────
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const loginError = document.getElementById('login-error');
const registerError = document.getElementById('register-error');

// ─── Login ───────────────────────────────────────────────────────
if (loginForm) {
  loginForm.addEventListener('submit', async e => {
    e.preventDefault();
    loginError.classList.add('hidden');

    const payload = {
      email: loginForm.email.value.trim(),
      password: loginForm.password.value.trim()
    };

    try {
      const res = await fetch(`${API}/users/login`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error('Login inválido');
      const data = await res.json();
      localStorage.setItem('user', JSON.stringify(data));
      window.location.href = '/dashboard';
    } catch (err) {
      loginError.textContent = 'Não foi possível conectar ao servidor ou login inválido.';
      loginError.classList.remove('hidden');
    }
  });
}

// ─── Registro ───────────────────────────────────────────────────
if (registerForm) {
  registerForm.addEventListener('submit', async e => {
    e.preventDefault();
    registerError.classList.add('hidden');

    const payload = {
      name: registerForm.name.value.trim(),
      email: registerForm.email.value.trim(),
      password: registerForm.password.value.trim()
    };

    try {
      const res = await fetch(`${API}/users/register`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error('Erro ao registrar');
      const data = await res.json();
      localStorage.setItem('user', JSON.stringify(data));
      window.location.href = '/dashboard';
    } catch (err) {
      registerError.textContent = 'Não foi possível conectar ao servidor ou email já cadastrado.';
      registerError.classList.remove('hidden');
    }
  });
}