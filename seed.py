from app import create_app
from app.extensions import db
from app.models import Usuario

app = create_app()

with app.app_context():
    db.create_all()

    if not Usuario.query.filter_by(username="admin").first():
        usuario = Usuario(username="admin", email="admin@agendamedica.com")
        usuario.senha = "admin123"
        db.session.add(usuario)
        db.session.commit()
        print("Usuário de teste criado: admin / admin123")
    else:
        print("Usuário de teste já existe.")
