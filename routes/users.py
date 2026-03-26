from flask import Blueprint, request, jsonify
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

users_bp = Blueprint('users', __name__)

# ─── Registro ───────────────────────────────
@users_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'error': 'Todos os campos são obrigatórios'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email já cadastrado'}), 400

    user = User(
        name=data['name'],
        email=data['email'],
        password=generate_password_hash(data['password'])
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({'id': user.id, 'name': user.name, 'email': user.email})

# ─── Login ─────────────────────────────────
@users_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data.get('email')).first()
    if not user or not check_password_hash(user.password, data.get('password')):
        return jsonify({'error': 'Login inválido'}), 401

    return jsonify({'id': user.id, 'name': user.name, 'email': user.email})