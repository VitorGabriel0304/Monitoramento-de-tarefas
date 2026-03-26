from flask import Blueprint, request, jsonify
from models import db, Task
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__)

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

# GET /api/tasks/<user_id>
@tasks_bp.route('/<int:user_id>', methods=['GET'])
def get_tasks(user_id):
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': t.id,
        'title': t.title,
        'description': t.description,
        'status': t.status,
        'priority': t.priority,
        'due_date': t.due_date.isoformat() if t.due_date else ''
    } for t in tasks])

# POST /api/tasks/
@tasks_bp.route('/', methods=['POST'])
def create_task():
    data = request.json
    task = Task(
        title=data['title'],
        description=data.get('description'),
        status=data.get('status', 'pending'),
        priority=data.get('priority', 'medium'),
        due_date=parse_date(data.get('due_date')),
        user_id=data['user_id']
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({'id': task.id}), 201

# PUT /api/tasks/<id>
@tasks_bp.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.json
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.status = data.get('status', task.status)
    task.priority = data.get('priority', task.priority)
    task.due_date = parse_date(data.get('due_date')) or task.due_date
    db.session.commit()
    return jsonify({'success': True})

# DELETE /api/tasks/<id>
@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'success': True})