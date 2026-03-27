// ─── API ─────────────────────────────────────
const API = window.location.hostname.includes('localhost')
  ? 'http://localhost:5000/api'
  : 'https://minhastafefas.up.railway.app/api';

// ─── Auth guard ──────────────────────────────
const user = JSON.parse(localStorage.getItem('user'));
if (!user) window.location.href = '/';

// ─── Estado ──────────────────────────────────
let tasks        = [];
let activeFilter = 'all';
let editingId    = null;

// ─── DOM ─────────────────────────────────────
const tasksList    = document.getElementById('tasks-list');
const emptyState   = document.getElementById('empty-state');
const modalOverlay = document.getElementById('modal-overlay');
const searchInput  = document.getElementById('search-input');

// ─── Init ─────────────────────────────────────
document.getElementById('user-name')  && (document.getElementById('user-name').textContent  = user.name);
document.getElementById('user-avatar') && (document.getElementById('user-avatar').textContent = user.name.charAt(0).toUpperCase());
setGreeting();
loadTasks();

// ─── Saudação ─────────────────────────────────
function setGreeting() {
  const h     = new Date().getHours();
  const greet = h < 12 ? 'Bom dia' : h < 18 ? 'Boa tarde' : 'Boa noite';
  const el    = document.getElementById('dash-greeting');
  if (el) el.textContent = `${greet}, ${user.name.split(' ')[0]}! 👋`;
  const opts  = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  const dateEl = document.getElementById('dash-date');
  if (dateEl) dateEl.textContent = new Date().toLocaleDateString('pt-BR', opts);
}

// ─── Carregar tarefas ─────────────────────────
async function loadTasks() {
  try {
    const res = await fetch(`${API}/tasks/${user.id}`);
    tasks = await res.json();
    renderAll();
  } catch {
    console.error('Erro ao carregar tarefas');
  }
}

// ─── Renderização ─────────────────────────────
function renderAll() {
  updateCounts();
  renderTasks();
}

function updateCounts() {
  const total   = tasks.length;
  const pending = tasks.filter(t => t.status === 'pending').length;
  const inProg  = tasks.filter(t => t.status === 'in_progress').length;
  const done    = tasks.filter(t => t.status === 'done').length;

  // Sidebar desktop
  setText('stat-all',        total);
  setText('stat-pending',    pending);
  setText('stat-in_progress', inProg);
  setText('stat-done',       done);
  setText('count-all',       total);
  setText('count-pending',   pending);
  setText('count-in_progress', inProg);
  setText('count-done',      done);

  // Bottom nav mobile badges
  setBadge('bnav-count-all',        total);
  setBadge('bnav-count-pending',    pending);
  setBadge('bnav-count-in_progress', inProg);
  setBadge('bnav-count-done',       done);
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function setBadge(id, val) {
  const el = document.getElementById(id);
  if (!el) return;
  if (val > 0) { el.textContent = val > 99 ? '99+' : val; el.style.display = 'block'; }
  else         { el.style.display = 'none'; }
}

function renderTasks() {
  const query  = searchInput ? searchInput.value.toLowerCase() : '';
  let filtered = activeFilter === 'all' ? tasks : tasks.filter(t => t.status === activeFilter);
  if (query) filtered = filtered.filter(t =>
    t.title.toLowerCase().includes(query) ||
    (t.description && t.description.toLowerCase().includes(query))
  );

  // Limpa mantendo empty-state
  Array.from(tasksList.children).forEach(c => { if (c.id !== 'empty-state') c.remove(); });

  if (filtered.length === 0) {
    tasksList.appendChild(emptyState);
    emptyState.classList.remove('hidden');
    return;
  }
  emptyState.classList.add('hidden');
  filtered.forEach(t => tasksList.appendChild(buildCard(t)));
}

function buildCard(task) {
  const card = document.createElement('div');
  card.className = 'task-card' + (task.status === 'done' ? ' done-card' : '');
  card.dataset.id = task.id;

  const statusLabel = { pending: 'Não iniciada', in_progress: 'Em andamento', done: 'Concluída' };
  const statusClass = { pending: 'badge-pending', in_progress: 'badge-progress', done: 'badge-done' };
  const prioClass   = { low: 'badge-low', medium: 'badge-medium', high: 'badge-high' };
  const prioLabel   = { low: '↓ Baixa', medium: '→ Média', high: '↑ Alta' };

  card.innerHTML = `
    <div class="task-left">
      <div class="task-meta">
        <span class="badge ${statusClass[task.status]}">${statusLabel[task.status]}</span>
        <span class="badge ${prioClass[task.priority]}">${prioLabel[task.priority]}</span>
        ${task.due_date ? `<span class="task-date">📅 ${formatDate(task.due_date)}</span>` : ''}
      </div>
      <div class="task-title">${escHtml(task.title)}</div>
      ${task.description ? `<div class="task-desc">${escHtml(task.description)}</div>` : ''}
    </div>
    <div class="task-actions">
      <select class="status-select" title="Alterar status">
        <option value="pending"     ${task.status === 'pending'     ? 'selected' : ''}>○ Não iniciada</option>
        <option value="in_progress" ${task.status === 'in_progress' ? 'selected' : ''}>◑ Em andamento</option>
        <option value="done"        ${task.status === 'done'        ? 'selected' : ''}>● Concluída</option>
      </select>
      <button class="btn-icon edit"   title="Editar">✏️</button>
      <button class="btn-icon delete" title="Excluir">🗑</button>
    </div>
  `;

  card.querySelector('.status-select').addEventListener('change', e => quickStatus(task.id, e.target.value));
  card.querySelector('.edit').addEventListener('click',   () => openModal(task));
  card.querySelector('.delete').addEventListener('click', () => deleteTask(task.id));
  return card;
}

// ─── Quick status ─────────────────────────────
async function quickStatus(id, status) {
  try {
    await fetch(`${API}/tasks/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    loadTasks();
  } catch { console.error('Erro ao atualizar'); }
}

// ─── Delete ──────────────────────────────────
async function deleteTask(id) {
  if (!confirm('Remover esta tarefa?')) return;
  try {
    await fetch(`${API}/tasks/${id}`, { method: 'DELETE' });
    loadTasks();
  } catch { console.error('Erro ao deletar'); }
}

// ─── Modal ────────────────────────────────────
function openModal(task = null) {
  editingId = task ? task.id : null;
  document.getElementById('modal-title').textContent   = task ? 'Editar tarefa' : 'Nova tarefa';
  document.getElementById('task-id').value             = task ? task.id : '';
  document.getElementById('task-title').value          = task ? task.title : '';
  document.getElementById('task-desc').value           = task ? (task.description || '') : '';
  document.getElementById('task-status').value         = task ? task.status : 'pending';
  document.getElementById('task-priority').value       = task ? task.priority : 'medium';
  document.getElementById('task-date').value           = task ? (task.due_date || '') : '';
  document.getElementById('task-error').classList.add('hidden');
  modalOverlay.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
  setTimeout(() => document.getElementById('task-title').focus(), 300);
}

function closeModal() {
  modalOverlay.classList.add('hidden');
  document.body.style.overflow = '';
  editingId = null;
}

async function saveTask() {
  const title = document.getElementById('task-title').value.trim();
  const errEl = document.getElementById('task-error');
  if (!title) { errEl.textContent = 'O título é obrigatório.'; errEl.classList.remove('hidden'); return; }
  errEl.classList.add('hidden');

  const payload = {
    user_id:     user.id,
    title,
    description: document.getElementById('task-desc').value.trim(),
    status:      document.getElementById('task-status').value,
    priority:    document.getElementById('task-priority').value,
    due_date:    document.getElementById('task-date').value || null
  };

  const btn = document.getElementById('btn-save-task');
  btn.disabled = true; btn.textContent = 'Salvando...';

  try {
    if (editingId) {
      await fetch(`${API}/tasks/${editingId}`, {
        method: 'PUT', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } else {
      await fetch(`${API}/tasks/`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    }
    closeModal();
    loadTasks();
  } catch {
    errEl.textContent = 'Erro ao salvar. Tente novamente.';
    errEl.classList.remove('hidden');
  } finally {
    btn.disabled = false; btn.textContent = 'Salvar';
  }
}

// ─── Filtro (sidebar + bottom nav) ────────────
function applyFilter(filter) {
  activeFilter = filter;
  const titles = { all: 'Todas as tarefas', pending: 'Não iniciadas', in_progress: 'Em andamento', done: 'Concluídas' };
  setText('tasks-section-title', titles[filter]);

  // Sidebar desktop
  document.querySelectorAll('.nav-item').forEach(i =>
    i.classList.toggle('active', i.dataset.filter === filter)
  );
  // Bottom nav mobile
  document.querySelectorAll('.bottom-nav-item[data-filter]').forEach(i =>
    i.classList.toggle('active', i.dataset.filter === filter)
  );

  renderTasks();
}

// ─── Listeners ────────────────────────────────

// Modal
document.getElementById('btn-new-task').addEventListener('click',    () => openModal());
document.getElementById('modal-close').addEventListener('click',     closeModal);
document.getElementById('btn-cancel-task').addEventListener('click', closeModal);
document.getElementById('btn-save-task').addEventListener('click',   saveTask);
modalOverlay.addEventListener('click', e => { if (e.target === modalOverlay) closeModal(); });
document.getElementById('task-title').addEventListener('keydown', e => { if (e.key === 'Enter') saveTask(); });

// Sidebar nav desktop
document.querySelectorAll('.nav-item').forEach(item =>
  item.addEventListener('click', () => applyFilter(item.dataset.filter))
);

// Bottom nav mobile
document.querySelectorAll('.bottom-nav-item[data-filter]').forEach(item =>
  item.addEventListener('click', () => applyFilter(item.dataset.filter))
);

// Logout (sidebar + bottom nav)
document.getElementById('btn-logout') && document.getElementById('btn-logout').addEventListener('click', doLogout);
document.getElementById('bnav-logout') && document.getElementById('bnav-logout').addEventListener('click', doLogout);
function doLogout() {
  if (confirm('Deseja sair?')) { localStorage.removeItem('user'); window.location.href = '/'; }
}

// Stat cards
document.querySelectorAll('.stat-card').forEach(card =>
  card.addEventListener('click', () => applyFilter(card.dataset.status))
);

// Busca
searchInput && searchInput.addEventListener('input', renderTasks);

// ─── Helpers ──────────────────────────────────
function escHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
function formatDate(str) {
  if (!str) return '';
  const [y,m,d] = str.split('-');
  return `${d}/${m}/${y}`;
}