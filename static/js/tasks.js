// ─── Configuração da API ─────────────────────────
const API = window.location.hostname.includes('localhost')
  ? 'http://localhost:5000/api'
  : 'https://minhastafefas.up.railway.app/api';

// ─── Auth guard ────────────────────────────────
const user = JSON.parse(localStorage.getItem('user'));
if (!user) window.location.href = '/';

// ─── Estado do App ─────────────────────────────
let tasks = [];
let activeFilter = 'all';
let editingId = null;

// ─── Referências do DOM ────────────────────────
const tasksList = document.getElementById('tasks-list');
const emptyState = document.getElementById('empty-state');
const modalOverlay = document.getElementById('modal-overlay');
const searchInput = document.getElementById('search-input');
const sidebarEl = document.querySelector('.sidebar');
const toggleBtn = document.getElementById('sidebar-toggle');
const backdropEl = document.getElementById('sidebar-backdrop');

// ─── Inicialização ─────────────────────────────
document.getElementById('user-name').textContent = user.name;
document.getElementById('user-avatar').textContent = user.name.charAt(0).toUpperCase();
setGreeting();
loadTasks();

// ─── Saudação e data ───────────────────────────
function setGreeting() {
  const h = new Date().getHours();
  const greet = h < 12 ? 'Bom dia' : h < 18 ? 'Boa tarde' : 'Boa noite';
  document.getElementById('dash-greeting').textContent = `${greet}, ${user.name.split(' ')[0]}! 👋`;
  const opts = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  document.getElementById('dash-date').textContent = new Date().toLocaleDateString('pt-BR', opts);
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
  const total = tasks.length;
  const pending = tasks.filter(t => t.status === 'pending').length;
  const inProgress = tasks.filter(t => t.status === 'in_progress').length;
  const done = tasks.filter(t => t.status === 'done').length;

  document.getElementById('stat-all').textContent = total;
  document.getElementById('stat-pending').textContent = pending;
  document.getElementById('stat-in_progress').textContent = inProgress;
  document.getElementById('stat-done').textContent = done;

  document.getElementById('count-all').textContent = total;
  document.getElementById('count-pending').textContent = pending;
  document.getElementById('count-in_progress').textContent = inProgress;
  document.getElementById('count-done').textContent = done;
}

function renderTasks() {
  const query = searchInput.value.toLowerCase();
  let filtered = activeFilter === 'all' ? tasks : tasks.filter(t => t.status === activeFilter);

  if (query) filtered = filtered.filter(t =>
    t.title.toLowerCase().includes(query) ||
    (t.description && t.description.toLowerCase().includes(query))
  );

  tasksList.innerHTML = '';
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
  const prioClass = { low: 'badge-low', medium: 'badge-medium', high: 'badge-high' };
  const prioLabel = { low: '↓ Baixa', medium: '→ Média', high: '↑ Alta' };

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
        <option value="pending"     ${task.status==='pending'?'selected':''}>○ Não iniciada</option>
        <option value="in_progress" ${task.status==='in_progress'?'selected':''}>◑ Em andamento</option>
        <option value="done"        ${task.status==='done'?'selected':''}>● Concluída</option>
      </select>
      <button class="btn-icon edit" title="Editar">✏️</button>
      <button class="btn-icon delete" title="Excluir">🗑</button>
    </div>
  `;

  card.querySelector('.status-select').addEventListener('change', e => quickStatus(task.id, e.target.value));
  card.querySelector('.edit').addEventListener('click', () => openModal(task));
  card.querySelector('.delete').addEventListener('click', () => deleteTask(task.id));
  return card;
}

// ─── Quick status ─────────────────────────────
async function quickStatus(id, status) {
  await fetch(`${API}/tasks/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status })
  });
  loadTasks();
}

// ─── Delete ──────────────────────────────────
async function deleteTask(id) {
  if (!confirm('Deseja remover esta tarefa?')) return;
  await fetch(`${API}/tasks/${id}`, { method: 'DELETE' });
  loadTasks();
}

// ─── Helpers ──────────────────────────────────
function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
function formatDate(str) {
  if (!str) return '';
  const [y,m,d] = str.split('-');
  return `${d}/${m}/${y}`;
}