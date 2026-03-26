# __init__.py dentro da pasta routes
from flask import Flask
from .users import users_bp
from .tasks import tasks_bp  # assumindo que você tenha tasks_bp em tasks.py

def create_app():
    app = Flask(__name__)

    # Configurações (exemplo, pode adicionar secret key, db URI etc)
    app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Registrar blueprints
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')

    return app