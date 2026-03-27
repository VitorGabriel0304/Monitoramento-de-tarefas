from flask import Blueprint, request, jsonify
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

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
    if not user or not check_password_hash(user.password, data.get('password', '')):
        return jsonify({'error': 'E-mail ou senha inválidos'}), 401

    return jsonify({'id': user.id, 'name': user.name, 'email': user.email})

# ─── Esqueceu a Senha ──────────────────────
@users_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data  = request.json
    email = data.get('email', '').strip()

    if not email:
        return jsonify({'error': 'Informe o e-mail'}), 400

    user = User.query.filter_by(email=email).first()

    # Sempre retorna 200 para não revelar se o e-mail existe
    if not user:
        return jsonify({'message': 'Se o e-mail estiver cadastrado, você receberá as instruções.'})

    # Gera token seguro e salva no usuário
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    db.session.commit()

    # ── Monta e-mail ──────────────────────────────────────────────
    reset_url  = f"{os.environ.get('APP_URL', 'http://localhost:5000')}/reset-password?token={token}"
    smtp_host  = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    smtp_port  = int(os.environ.get('SMTP_PORT', 587))
    smtp_user  = os.environ.get('SMTP_USER', '')   # seu e-mail no Railway env
    smtp_pass  = os.environ.get('SMTP_PASS', '')   # senha de app no Railway env

    html_body = f"""
    <div style="font-family: 'Segoe UI', sans-serif; max-width: 520px; margin: auto; background: #111115;
                border: 1px solid #25252f; border-radius: 16px; padding: 36px; color: #ebebf0;">
      <h2 style="color:#a78bfa; font-size:22px; margin-bottom:8px;">TaskFlow</h2>
      <p style="font-size:15px; color:#7a7a92; margin-bottom:24px;">Recuperação de senha</p>
      <p style="font-size:15px;">Olá, <strong>{user.name}</strong>!</p>
      <p style="font-size:14px; color:#ebebf0; margin:16px 0;">
        Recebemos uma solicitação para redefinir sua senha. Clique no botão abaixo para criar uma nova senha.
        Este link expira em <strong>1 hora</strong>.
      </p>
      <a href="{reset_url}"
         style="display:inline-block; background:#7c5cfc; color:#fff; text-decoration:none;
                padding:12px 28px; border-radius:10px; font-weight:700; font-size:14px; margin:8px 0 24px;">
        Redefinir senha
      </a>
      <p style="font-size:12px; color:#7a7a92;">
        Se você não solicitou a recuperação de senha, ignore este e-mail.<br/>
        O link é válido por 1 hora.
      </p>
    </div>
    """

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'TaskFlow — Recuperação de senha'
        msg['From']    = smtp_user
        msg['To']      = email
        msg.attach(MIMEText(html_body, 'html'))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, email, msg.as_string())

    except Exception as e:
        # Log interno, mas não expõe o erro ao usuário
        print(f'[SMTP ERROR] {e}')
        # Ainda retorna sucesso para não revelar infra
        pass

    return jsonify({'message': 'Se o e-mail estiver cadastrado, você receberá as instruções.'})

# ─── Redefinir Senha ───────────────────────
@users_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data     = request.json
    token    = data.get('token', '').strip()
    password = data.get('password', '').strip()

    if not token or not password:
        return jsonify({'error': 'Token e nova senha são obrigatórios'}), 400

    if len(password) < 6:
        return jsonify({'error': 'A senha deve ter pelo menos 6 caracteres'}), 400

    user = User.query.filter_by(reset_token=token).first()
    if not user:
        return jsonify({'error': 'Link inválido ou expirado'}), 400

    user.password    = generate_password_hash(password)
    user.reset_token = None
    db.session.commit()

    return jsonify({'message': 'Senha redefinida com sucesso!'})