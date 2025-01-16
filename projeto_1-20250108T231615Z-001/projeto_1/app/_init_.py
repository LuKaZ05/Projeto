from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = b'\x9f\x8b\x1d\x8f\x9e\x1d\x8f\x9e\x1d\x8f\x9e\x1d\x8f\x9e\x1d\x8f\x9e\x1d\x8f\x9e\x1d\x8f\x9e\x1d\x8f\x9e\x1d\x8f\x9e'

    db.init_app(app)

    with app.app_context():
        from . import models
        from .routes import main
        app.register_blueprint(main)
        print(app.url_map)
        db.create_all()  # Cria todas as tabelas

    return app