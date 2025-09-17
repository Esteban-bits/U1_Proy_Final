from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'  

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario = db.Column(db.String(20), unique=True, nullable=False)
    contraseña = db.Column(db.String(15), nullable=False)

    def __init__(self, usuario, contraseña):
        self.usuario = usuario
        self.contraseña = contraseña