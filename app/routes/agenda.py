import logging
from flask import Blueprint, render_template, jsonify, request, session
from app.utils import login_requerido, api_login_requerido
from app.services.api_client import buscar_agendamentos, ApiIndisponivelError

logger = logging.getLogger(__name__)
agenda_bp = Blueprint("agenda", __name__)


@agenda_bp.route("/agenda")
@login_requerido
def pagina_agenda():
    return render_template("agenda.html", usuario_nome=session.get("usuario_nome"))


@agenda_bp.route("/api/agendamentos")
@api_login_requerido
def api_agendamentos():
    termo = (request.args.get("q") or "").strip()

    try:
        agendamentos = buscar_agendamentos(termo_busca=termo or None)
    except ApiIndisponivelError as exc:
        logger.error("Erro ao buscar agendamentos: %s", exc)
        return jsonify({"erro": str(exc)}), 503

    if not agendamentos:
        return jsonify({"agendamentos": [], "mensagem": "Nenhum agendamento encontrado."}), 200

    return jsonify({"agendamentos": agendamentos}), 200