// ─── Configuração da API ─────────────────────────
const API = window.location.hostname.includes('localhost')
  ? 'http://localhost:5000/api'
  : 'https://minhastafefas.up.railway.app/api';

// ─── Tabs ─────────────────────────────────────────
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
  });
});

// ─── Helpers ─────────────────────────────────────
function showError(id, msg) {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.classList.remove('hidden');
}
function hideMsg(id) {
  document.getElementById(id).classList.add('hidden');
}
function setLoading(btn, loading) {
  btn.disabled = loading;
  btn.style.opacity = loading ? '.6' : '1';
  btn.textContent = loading ? 'Aguarde...' : btn.dataset.label;
}

// ─── Login ───────────────────────────────────────
const btnLogin = document.getElementById('btn-login');
btnLogin.dataset.label = btnLogin.textContent;

btnLogin.addEventListener('click', async () => {
  hideMsg('login-error');
  const email    = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value.trim();

  if (!email || !password) {
    showError('login-error', 'Preencha e-mail e senha.');
    return;
  }

  setLoading(btnLogin, true);
  try {
    const res = await fetch(`${API}/users/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Login inválido');
    localStorage.setItem('user', JSON.stringify(data));
    window.location.href = '/dashboard';
  } catch (err) {
    showError('login-error', err.message || 'Não foi possível conectar ao servidor.');
  } finally {
    setLoading(btnLogin, false);
  }
});

// Enter no campo senha dispara login
document.getElementById('login-password').addEventListener('keydown', e => {
  if (e.key === 'Enter') btnLogin.click();
});

// ─── Registro ────────────────────────────────────
const btnRegister = document.getElementById('btn-register');
btnRegister.dataset.label = btnRegister.textContent;

btnRegister.addEventListener('click', async () => {
  hideMsg('reg-error');
  hideMsg('reg-success');

  const name     = document.getElementById('reg-name').value.trim();
  const email    = document.getElementById('reg-email').value.trim();
  const password = document.getElementById('reg-password').value.trim();

  if (!name || !email || !password) {
    showError('reg-error', 'Preencha todos os campos.');
    return;
  }
  if (password.length < 6) {
    showError('reg-error', 'A senha deve ter pelo menos 6 caracteres.');
    return;
  }

  setLoading(btnRegister, true);
  try {
    const res = await fetch(`${API}/users/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Erro ao registrar');
    localStorage.setItem('user', JSON.stringify(data));
    window.location.href = '/dashboard';
  } catch (err) {
    showError('reg-error', err.message || 'Não foi possível conectar ao servidor.');
  } finally {
    setLoading(btnRegister, false);
  }
});

// ─── Esqueceu a senha ─────────────────────────────
const btnForgot   = document.getElementById('btn-forgot');
const forgotPanel = document.getElementById('forgot-panel');

if (btnForgot) {
  btnForgot.addEventListener('click', () => {
    // Esconde login, mostra painel de recuperação
    document.getElementById('tab-login').classList.remove('active');
    forgotPanel.classList.add('active');
    // Remove active das tabs visuais
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  });
}

const btnBackLogin = document.getElementById('btn-back-login');
if (btnBackLogin) {
  btnBackLogin.addEventListener('click', () => {
    forgotPanel.classList.remove('active');
    document.getElementById('tab-login').classList.add('active');
    document.querySelector('[data-tab="login"]').classList.add('active');
    hideMsg('forgot-error');
    hideMsg('forgot-success');
  });
}

const btnSendReset = document.getElementById('btn-send-reset');
if (btnSendReset) {
  btnSendReset.dataset.label = btnSendReset.textContent;
  btnSendReset.addEventListener('click', async () => {
    hideMsg('forgot-error');
    hideMsg('forgot-success');
    const email = document.getElementById('forgot-email').value.trim();
    if (!email) {
      showError('forgot-error', 'Informe seu e-mail.');
      return;
    }

    setLoading(btnSendReset, true);
    try {
      const res = await fetch(`${API}/users/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Erro ao enviar e-mail');
      // Mostra mensagem de sucesso
      const successEl = document.getElementById('forgot-success');
      successEl.textContent = 'Se este e-mail estiver cadastrado, você receberá as instruções em breve.';
      successEl.classList.remove('hidden');
    } catch (err) {
      showError('forgot-error', err.message || 'Erro ao processar solicitação.');
    } finally {
      setLoading(btnSendReset, false);
    }
  });
}