from flask import Blueprint, request, jsonify
from models import db, Task

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/<int:user_id>', methods=['GET'])
def get_tasks(user_id):
    tasks = Task.query.filter_by(user_id=user_id).order_by(Task.created.desc()).all()
    return jsonify([t.to_dict() for t in tasks]), 200


@tasks_bp.route('/', methods=['POST'])
def create_task():
    data = request.get_json()
    if not data.get('title') or not data.get('user_id'):
        return jsonify({'error': 'Título e usuário são obrigatórios.'}), 400

    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        status=data.get('status', 'pending'),
        priority=data.get('priority', 'medium'),
        due_date=data.get('due_date', ''),
        user_id=data['user_id']
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({'message': 'Tarefa criada!', 'task': task.to_dict()}), 201


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    task.title       = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.status      = data.get('status', task.status)
    task.priority    = data.get('priority', task.priority)
    task.due_date    = data.get('due_date', task.due_date)
    db.session.commit()
    return jsonify({'message': 'Tarefa atualizada!', 'task': task.to_dict()}), 200


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Tarefa removida!'}), 200