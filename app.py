import os
from flask import Flask, render_template
from flask_cors import CORS
from models import db
from routes.users import users_bp
from routes.tasks import tasks_bp

app = Flask(__name__)

# Configuracoes
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'taskmanager-secret-2024')

database_url = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db.init_app(app)

app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(tasks_bp, url_prefix='/api/tasks')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', debug=False, port=port)