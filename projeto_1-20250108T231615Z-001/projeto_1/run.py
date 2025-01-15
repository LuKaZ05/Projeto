from app._init_ import create_app, db
from app.models import User, Doctor, Patient, Appointment

app = create_app()
if __name__ == "__main__":
    app.run(debug=True)
with app.app_context():
    db.create_all()  # Cria as tabelas no banco de dados
    print("Banco de dados criado com sucesso!")
