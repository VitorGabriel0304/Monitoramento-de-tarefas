from flask import Blueprint, request, jsonify
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import os
import urllib.request
import urllib.error
import json

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

    # Sempre retorna 200 — não revela se o e-mail existe
    if not user:
        return jsonify({'message': 'Se o e-mail estiver cadastrado, você receberá as instruções.'})

    token = secrets.token_urlsafe(32)
    user.reset_token = token
    db.session.commit()

    app_url   = os.environ.get('APP_URL', 'http://localhost:5000')
    reset_url = f"{app_url}/reset-password?token={token}"

    html_body = f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#0b0b0e;font-family:'Segoe UI',sans-serif;">
  <div style="max-width:520px;margin:40px auto;background:#111115;border:1px solid #25252f;border-radius:20px;padding:40px;">
    <div style="margin-bottom:28px;">
      <span style="font-size:24px;color:#a78bfa;font-weight:800;">&#11041; TaskFlow</span>
    </div>
    <h2 style="color:#ebebf0;font-size:22px;font-weight:700;margin:0 0 8px;">Recuperar senha</h2>
    <p style="color:#7a7a92;font-size:14px;margin:0 0 28px;">
      Ol&aacute;, <strong style="color:#ebebf0;">{user.name}</strong>!
      Recebemos uma solicita&ccedil;&atilde;o para redefinir sua senha.
    </p>
    <a href="{reset_url}"
       style="display:block;background:#7c5cfc;color:#fff;text-decoration:none;
              text-align:center;padding:14px 28px;border-radius:12px;
              font-weight:700;font-size:15px;margin-bottom:28px;">
      Redefinir minha senha
    </a>
    <p style="color:#7a7a92;font-size:12px;line-height:1.8;margin:0;">
      Se voc&ecirc; n&atilde;o solicitou, ignore este e-mail.<br/>
      Este link expira em <strong style="color:#ebebf0;">1 hora</strong>.
    </p>
    <hr style="border:none;border-top:1px solid #25252f;margin:24px 0;"/>
    <p style="color:#3d3d4f;font-size:11px;margin:0;">TaskFlow &mdash; Gerenciador de tarefas</p>
  </div>
</body>
</html>
"""

    _send_resend(to=email, subject='TaskFlow — Recuperação de senha', html=html_body)

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


# ─── Helper Resend ────────────────────────
def _send_resend(to, subject, html):
    api_key = os.environ.get('RESEND_API_KEY', '')
    if not api_key:
        print('[RESEND] RESEND_API_KEY não configurada — e-mail não enviado')
        return

    # Use onboarding@resend.dev para testes sem domínio próprio
    # Quando tiver domínio verificado, troque pelo seu
    sender = os.environ.get('RESEND_FROM', 'TaskFlow <onboarding@resend.dev>')

    payload = json.dumps({
        'from':    sender,
        'to':      [to],
        'subject': subject,
        'html':    html
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.resend.com/emails',
        data=payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type':  'application/json'
        },
        method='POST'
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            print(f'[RESEND] Enviado com sucesso: {result.get("id")}')
    except urllib.error.HTTPError as e:
        print(f'[RESEND] Erro HTTP {e.code}: {e.read().decode()}')
    except Exception as e:
        print(f'[RESEND] Erro inesperado: {e}')