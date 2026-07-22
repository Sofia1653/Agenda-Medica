from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class Usuario(db.Model):
    """Tabela de usuários usada para autenticação (login)."""
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)


class LogAcesso(db.Model):
    """Registra tentativas de login (sucesso/falha) para auditoria e depuração."""
    __tablename__ = "logs_acesso"

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(120))
    sucesso = db.Column(db.Boolean, default=False)
    detalhe = db.Column(db.String(255))