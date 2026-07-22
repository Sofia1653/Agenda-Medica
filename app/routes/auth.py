import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from app.models import Usuario, LogAcesso

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    if session.get("usuario_id"):
        return redirect(url_for("agenda.pagina_agenda"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    identificador = (request.form.get("usuario") or "").strip()
    senha = request.form.get("senha") or ""

    if not identificador or not senha:
        flash("Informe usuário/e-mail e senha.", "erro")
        return render_template("login.html"), 400

    try:
        usuario = Usuario.query.filter(
            (Usuario.username == identificador) | (Usuario.email == identificador)
        ).first()

        credenciais_validas = usuario is not None and usuario.checar_senha(senha)

        db.session.add(LogAcesso(
            usuario=identificador,
            sucesso=credenciais_validas,
            detalhe="login via formulário",
        ))
        db.session.commit()

    except SQLAlchemyError as exc:
        logger.error("Erro de conexão/consulta ao banco de dados durante login: %s", exc)
        flash("Não foi possível acessar o banco de dados no momento. Tente novamente em instantes.", "erro")
        return render_template("login.html"), 500

    if not credenciais_validas:
        logger.info('Tentativa de login inválida para "%s"', identificador)
        flash("Usuário ou senha inválidos.", "erro")
        return render_template("login.html"), 401

    session["usuario_id"] = usuario.id
    session["usuario_nome"] = usuario.username
    logger.info("Login bem-sucedido: %s", usuario.username)
    return redirect(url_for("agenda.pagina_agenda"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))