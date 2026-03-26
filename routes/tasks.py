const API = '/api';

const user = JSON.parse(localStorage.getItem('user'));
if (!user) window.location.href = '/';

let tasks        = [];
let activeFilter = 'all';
let editingId    = null;

const tasksList    = document.getElementById('tasks-list');
const emptyState   = document.getElementById('empty-state');
const modalOverlay = document.getElementById('modal-overlay');
const searchInput  = document.getElementById('search-input');

const sidebarEl  = document.getElementById('sidebar');
const toggleBtn  = document.getElementById('sidebar-toggle');
const backdropEl = document.getElementById('sidebar-backdrop');

toggleBtn.addEventListener('click', () => {
  sidebarEl.classList.toggle('open');
  backdropEl.classList.toggle('open');
});
backdropEl.addEventListener('click', () => {
  sidebarEl.classList.remove('open');
  backdropEl.classList.remove('open');
});

document.getElementById('user-name').textContent   = user.name;
document.getElementById('user-avatar').textContent = user.name.charAt(0).toUpperCase();
setGreeting();
loadTasks();

function setGreeting() {
  const h = new Date().getHours();
  const greet = h < 12 ? 'Bom dia' : h < 18 ? 'Boa tarde' : 'Boa noite';
  document.getElementById('dash-greeting').textContent = `${greet}, ${user.name.split(' ')[0]}! 👋`;
  const opts = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  document.getElementById('dash-date').textContent = new Date().toLocaleDateString('pt-BR', opts);
}

async function loadTasks() {
  try {
    const res = await fetch(`${API}/tasks/${user.id}`);
    tasks = await res.json();
    renderAll();
  } catch { console.error('Erro ao carregar tarefas'); }
}

function renderAll() { updateCounts(); renderTasks(); }

function updateCounts() {
  const total   = tasks.length;
  const pending = tasks.filter(t => t.status === 'pending').length;
  const prog    = tasks.filter(t => t.status === 'in_progress').length;
  const done    = tasks.filter(t => t.status === 'done').length;
  ['all','pending','in_progress','done'].forEach(k => {
    const v = k==='all'?total : k==='pending'?pending : k==='in_progress'?prog : done;
    document.getElementById('stat-'+k).textContent  = v;
    document.getElementById('count-'+k).textContent = v;
  });
}

function renderTasks() {
  const query  = searchInput.value.toLowerCase();
  let filtered = activeFilter === 'all' ? tasks : tasks.filter(t => t.status === activeFilter);
  if (query) filtered = filtered.filter(t =>
    t.title.toLowerCase().includes(query) || t.description.toLowerCase().includes(query)
  );
  tasksList.innerHTML = '';
  if (filtered.length === 0) { tasksList.appendChild(emptyState); emptyState.classList.remove('hidden'); return; }
  emptyState.classList.add('hidden');
  filtered.forEach(t => tasksList.appendChild(buildCard(t)));
}

function buildCard(task) {
  const card = document.createElement('div');
  card.className = 'task-card' + (task.status === 'done' ? ' done-card' : '');
  const sLabel = { pending:'Não iniciada', in_progress:'Em andamento', done:'Concluída' };
  const sCls   = { pending:'badge-pending', in_progress:'badge-progress', done:'badge-done' };
  const pCls   = { low:'badge-low', medium:'badge-medium', high:'badge-high' };
  const pLabel = { low:'↓ Baixa', medium:'→ Média', high:'↑ Alta' };
  card.innerHTML = `
    <div class="task-left">
      <div class="task-meta">
        <span class="badge ${sCls[task.status]}">${sLabel[task.status]}</span>
        <span class="badge ${pCls[task.priority]}">${pLabel[task.priority]}</span>
        ${task.due_date ? `<span class="task-date">📅 ${fmt(task.due_date)}</span>` : ''}
      </div>
      <div class="task-title">${esc(task.title)}</div>
      ${task.description ? `<div class="task-desc">${esc(task.description)}</div>` : ''}
    </div>
    <div class="task-actions">
      <select class="status-select">
        <option value="pending"     ${task.status==='pending'?'selected':''}>○ Não iniciada</option>
        <option value="in_progress" ${task.status==='in_progress'?'selected':''}>◑ Em andamento</option>
        <option value="done"        ${task.status==='done'?'selected':''}>● Concluída</option>
      </select>
      <button class="btn-icon edit" title="Editar">✏️</button>
      <button class="btn-icon delete" title="Excluir">🗑</button>
    </div>`;
  card.querySelector('.status-select').addEventListener('change', e => quickStatus(task.id, e.target.value));
  card.querySelector('.edit').addEventListener('click', () => openModal(task));
  card.querySelector('.delete').addEventListener('click', () => deleteTask(task.id));
  return card;
}

async function quickStatus(id, status) {
  await fetch(`${API}/tasks/${id}`, { method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify({status}) });
  loadTasks();
}

async function deleteTask(id) {
  if (!confirm('Deseja remover esta tarefa?')) return;
  await fetch(`${API}/tasks/${id}`, { method: 'DELETE' });
  loadTasks();
}

document.getElementById('btn-new-task').addEventListener('click', () => openModal());
document.getElementById('modal-close').addEventListener('click', closeModal);
document.getElementById('btn-cancel-task').addEventListener('click', closeModal);
modalOverlay.addEventListener('click', e => { if (e.target === modalOverlay) closeModal(); });

function openModal(task = null) {
  editingId = task ? task.id : null;
  document.getElementById('modal-title').textContent = task ? 'Editar tarefa' : 'Nova tarefa';
  document.getElementById('task-title').value    = task ? task.title : '';
  document.getElementById('task-desc').value     = task ? task.description : '';
  document.getElementById('task-status').value   = task ? task.status : 'pending';
  document.getElementById('task-priority').value = task ? task.priority : 'medium';
  document.getElementById('task-date').value     = task ? task.due_date : '';
  document.getElementById('task-error').classList.add('hidden');
  modalOverlay.classList.remove('hidden');
  document.getElementById('task-title').focus();
}
function closeModal() { modalOverlay.classList.add('hidden'); editingId = null; }

document.getElementById('btn-save-task').addEventListener('click', async () => {
  const title = document.getElementById('task-title').value.trim();
  const errEl = document.getElementById('task-error');
  errEl.classList.add('hidden');
  if (!title) { errEl.textContent = 'O título é obrigatório.'; errEl.classList.remove('hidden'); return; }
  const payload = {
    title,
    description: document.getElementById('task-desc').value.trim(),
    status:      document.getElementById('task-status').value,
    priority:    document.getElementById('task-priority').value,
    due_date:    document.getElementById('task-date').value,
    user_id:     user.id
  };
  try {
    if (editingId) {
      await fetch(`${API}/tasks/${editingId}`, { method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
    } else {
      await fetch(`${API}/tasks/`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
    }
    closeModal(); loadTasks();
  } catch { errEl.textContent = 'Erro ao salvar.'; errEl.classList.remove('hidden'); }
});

document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', () => {
    document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
    item.classList.add('active');
    activeFilter = item.dataset.filter;
    updateSectionTitle(); renderTasks();
    sidebarEl.classList.remove('open'); backdropEl.classList.remove('open');
  });
});

document.querySelectorAll('.stat-card').forEach(card => {
  card.addEventListener('click', () => {
    activeFilter = card.dataset.status;
    document.querySelectorAll('.nav-item').forEach(i => i.classList.toggle('active', i.dataset.filter === activeFilter));
    updateSectionTitle(); renderTasks();
  });
});

function updateSectionTitle() {
  const t = { all:'Todas as tarefas', pending:'Não iniciadas', in_progress:'Em andamento', done:'Concluídas' };
  document.getElementById('tasks-section-title').textContent = t[activeFilter] || 'Tarefas';
}

searchInput.addEventListener('input', () => renderTasks());

document.getElementById('btn-logout').addEventListener('click', () => {
  localStorage.removeItem('user'); window.location.href = '/';
});

function esc(s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function fmt(s) { if (!s) return ''; const [y,m,d] = s.split('-'); return `${d}/${m}/${y}`; }