from flask import Blueprint, request, jsonify
from models import db, Task

tasks_bp = Blueprint('tasks', __name__)

# ─── Listar tarefas do usuário ───────────────
@tasks_bp.route('/<int:user_id>', methods=['GET'])
def get_tasks(user_id):
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': t.id,
        'title': t.title,
        'description': t.description,
        'status': t.status,
        'priority': t.priority,
        'due_date': t.due_date
    } for t in tasks])

# ─── Criar nova tarefa ───────────────────────
@tasks_bp.route('/', methods=['POST'])
def create_task():
    data = request.json
    task = Task(
        user_id=data['user_id'],
        title=data['title'],
        description=data.get('description', ''),
        status=data.get('status', 'pending'),
        priority=data.get('priority', 'medium'),
        due_date=data.get('due_date', None)
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({'id': task.id})

# ─── Atualizar tarefa ───────────────────────
@tasks_bp.route('/<int:id>', methods=['PUT'])
def update_task(id):
    task = Task.query.get_or_404(id)
    data = request.json
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.status = data.get('status', task.status)
    task.priority = data.get('priority', task.priority)
    task.due_date = data.get('due_date', task.due_date)
    db.session.commit()
    return jsonify({'message': 'Atualizado'})

# ─── Deletar tarefa ─────────────────────────
@tasks_bp.route('/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Removido'})