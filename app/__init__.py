import os
import logging
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

from app.extensions import db

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-troque-em-producao")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///" + os.path.join(os.getcwd(), "data", "agenda.db")
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MOCK_API_URL"] = os.getenv("MOCK_API_URL", "http://localhost:5001")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger = logging.getLogger(__name__)

    db.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.agenda import agenda_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(agenda_bp)

    with app.app_context():
        try:
            db.create_all()
        except Exception as exc:  # erro de conexão com o banco na inicialização
            logger.error("Erro ao inicializar o banco de dados: %s", exc)

    @app.errorhandler(404)
    def nao_encontrado(e):
        return render_template("erro.html", titulo="Página não encontrada",
                                mensagem="O endereço acessado não existe."), 404

    @app.errorhandler(500)
    def erro_interno(e):
        logger.error("Erro interno não tratado: %s", e)
        if request.path.startswith("/api/"):
            return jsonify({"erro": "Erro interno no servidor."}), 500
        return render_template("erro.html", titulo="Erro interno",
                                mensagem="Algo deu errado. Tente novamente em instantes."), 500

    return app