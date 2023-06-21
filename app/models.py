from .extensions import db 
import datetime
from flask import Flask
from flask_security import UserMixin, RoleMixin
app = Flask(__name__)

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('usuarios.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class Users(db.Model, UserMixin):

    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user = db.Column(db.Text, unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True)
    password = db.Column(db.Text, nullable=False)
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


    def __init__(self, user, email, password, roles=None, active=True):
        self.user=user
        self.email = email
        self.password = password
        self.active = active
        if roles is None:
            roles = []
        self.roles = roles

    def __repr__(self):
        return f'{self.id, self.user, self.password}'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user,
            'password': self.password,
            'roles': self.roles
        }
    
    def is_active(self):
        # Devuelve True si el usuario está activo, de lo contrario, False
        return self.active  # o implementa tu lógica para determinar si el usuario está activo
    
    def get_id(self):
        # Devuelve el ID del usuario como una cadena
        return str(self.id)

class CategoriaGasto(db.Model):

    __tablename__ = 'categoria_gasto'

    categoria_id = db.Column(db.Integer, autoincrement=True ,primary_key=True)
    categoria = db.Column(db.Text, nullable=False)

    def __init__(self, categoria):
        self.categoria = categoria
    
    def __repr__(self):
        return f'{self.categoria_id, self.categoria}'
    
    def to_dict(self):
        return {
            'categoria_id': self.categoria_id,
            'categoria': self.categoria
        }

class Gastos(db.Model):

    __tablename__ = 'gastos'

    gasto_id = db.Column(db.Integer, autoincrement=True ,primary_key=True)
    description = db.Column(db.Text, nullable=False)
    monto = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.Date(), nullable=False)
    categoria = db.Column(db.Integer, db.ForeignKey(CategoriaGasto.categoria_id), nullable=False)

    #Relaciones
    categoria_rel = db.relationship('CategoriaGasto', backref=db.backref('categoria_gasto', lazy=True))

    def __init__(self, description, monto, fecha, categoria):
        self.description = description
        self.monto = monto
        self.fecha = fecha
        self.categoria = categoria

    def __repr__(self):
        return f'{self.description, self.monto, self.fecha, self.categoria}'
    
    def to_dict(self):
        return {
            'description': self.description,
            'monto': self.monto,
            'fecha': self.fecha,
            'categoria': self.categoria
        }

class CategoriaInversion(db.Model):

    __tablename__ = 'categoria_inversion'

    categoria_inv_id = db.Column(db.Integer, autoincrement=True ,primary_key=True)
    categoria_inv = db.Column(db.Text, nullable=False)

    def __init__(self, categoria_inv):
        self.categoria_inv = categoria_inv
    
    def __repr__(self):
        return f'{self.categoria_inv_id, self.categoria_inv}'
    
    def to_dict(self):
        return {
            'categoria_inv_id': self.categoria_inv_id,
            'categoria_inv': self.categoria_inv
        }

class Inversion(db.Model):
    __tablename__ = 'inversion'

    inversion_id = db.Column(db.Integer, autoincrement=True ,primary_key=True)
    description = db.Column(db.Text, nullable=False)
    monto = db.Column(db.Integer, nullable=False)
    rentab_esperada = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.Date(), nullable=False)
    categoria = db.Column(db.Integer, db.ForeignKey(CategoriaInversion.categoria_inv_id), nullable=False)

    #Relaciones
    categoria_rel = db.relationship('CategoriaInversion', backref=db.backref('categoria_inversion', lazy=True))
