from flask import Flask, render_template
from flask_cors import CORS
from models import db
from routes.users import users_bp
from routes.tasks import tasks_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'taskmanager-secret-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db.init_app(app)

app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(tasks_bp, url_prefix='/api/tasks')

# ── Rotas que servem o HTML ──────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# ── Cria tabelas e sobe o servidor ──────────────────────────
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)