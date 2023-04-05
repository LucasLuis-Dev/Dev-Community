from comunidade_dev import database, loginManager
from datetime import datetime
from flask_login import UserMixin


class Usuario(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False)
    senha = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True)
    fotoPerfil = database.Column(database.String, default='default.jpg')
    post = database.relationship('Post', backref='autor', lazy=True)
    comentario = database.relationship('Comentario', backref='autor', lazy=True)
    stacks = database.Column(database.String, nullable=False, default='Não informado')
    areas = database.Column(database.String, nullable=False, default='Não informado')

    def contarPosts(self):
        return len(self.post)

class Post(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    titulo = database.Column(database.String, nullable=False)
    fotoPost = database.Column(database.String)
    corpo = database.Column(database.Text, nullable=False)
    dataCriacao = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)
    idUsuario = database.Column(database.Integer,  database.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    comentarios = database.relationship('Comentario', backref='post', cascade='all, delete-orphan', lazy=True)


class Comentario(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    corpo = database.Column(database.Text, nullable=False)
    idPost = database.Column(database.Integer,  database.ForeignKey('post.id' , ondelete='CASCADE'))
    idUsuario = database.Column(database.Integer,  database.ForeignKey('usuario.id', ondelete='CASCADE'))
    dataCriacao = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)

from comunidade_dev import loginManager

@loginManager.user_loader
def loadUsuario(idUsuario):
    return Usuario.query.get(int(idUsuario))

