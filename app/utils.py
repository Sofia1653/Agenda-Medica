from functools import wraps
from flask import session, redirect, url_for, jsonify, request


def login_requerido(view_func):
    """Protege rotas de página: se não estiver logado, manda pro /login."""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("usuario_id"):
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)
    return wrapper


def api_login_requerido(view_func):
    """Protege rotas de API (chamadas via JS): responde 401 em JSON, não redireciona."""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("usuario_id"):
            return jsonify({"erro": "Sessão expirada. Faça login novamente."}), 401
        return view_func(*args, **kwargs)
    return wrapper