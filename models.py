from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(100), nullable=False)
    email    = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created  = db.Column(db.DateTime, default=datetime.utcnow)
    tasks    = db.relationship('Task', backref='owner', lazy=True)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'email': self.email}


class Task(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    status      = db.Column(db.String(20), default='pending')   # pending | in_progress | done
    priority    = db.Column(db.String(10), default='medium')    # low | medium | high
    due_date    = db.Column(db.String(20), default='')
    created     = db.Column(db.DateTime, default=datetime.utcnow)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date,
            'created': self.created.strftime('%Y-%m-%d %H:%M'),
            'user_id': self.user_id,
        }