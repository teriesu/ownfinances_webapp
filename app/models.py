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

class Bienes(db.Model):
    __tablename__ = 'bienes'

    bien_id = db.Column(db.Integer, autoincrement=True ,primary_key=True)
    description = db.Column(db.Text, nullable=False)
    valor_inicial = db.Column(db.Integer, nullable=False)
    valor_venta = db.Column(db.Integer, nullable=True)


    def __init__(self, description, valor_inicial):
        self.description = description
        self.valor_inicial = valor_inicial
    
    def __repr__(self):
        return f'{self.description, self.valor_inicial}'
    
    def to_dict(self):
        return {
            'description': self.description,
            'valor_inicial': self.valor_inicial
        }

class Gastos(db.Model):

    __tablename__ = 'gastos'

    gasto_id = db.Column(db.Integer, autoincrement=True ,primary_key=True)
    description = db.Column(db.Text, nullable=False)
    monto = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.Date(), nullable=False)
    categoria = db.Column(db.Integer, db.ForeignKey(CategoriaGasto.categoria_id), nullable=False)
    hash_formato = db.Column(db.Text, nullable=True)
    id_df_formato = db.Column(db.Integer, nullable=True)
    id_patrimonio = db.Column(db.Integer, db.ForeignKey(Bienes.bien_id), nullable=True)
    essential = db.Column(db.Boolean, nullable=False)

    #Relaciones
    categoria_rel = db.relationship('CategoriaGasto', backref=db.backref('categoria_gasto', lazy=True))
    bien_rel = db.relationship('Bienes', backref=db.backref('gastos_bienes', lazy=True))

    def __init__(self, description, monto, fecha, categoria, hash_formato, id_df_formato, id_patrimonio, essential):
        self.description = description
        self.monto = monto
        self.fecha = fecha
        self.categoria = categoria
        self.hash_formato = hash_formato
        self.id_df_formato = id_df_formato
        self.id_patrimonio = id_patrimonio
        self.essential = essential

    def __repr__(self):
        return f'{self.description, self.monto, self.fecha, self.categoria, self.hash_formato, self.id_df_formato, self.id_patrimonio, self.essential}'
    
    def to_dict(self):
        return {
            'description': self.description,
            'monto': self.monto,
            'fecha': self.fecha,
            'categoria': self.categoria,
            'hash_formato': self.hash_formato,
            'id_df_formato': self.id_df_formato,
            'id_patrimonio': self.id_patrimonio,
            'essential': self.essential
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
    hash_formato = db.Column(db.Text, nullable=True)
    id_df_formato = db.Column(db.Integer, nullable=True)

    #Relaciones
    categoria_rel = db.relationship('CategoriaInversion', backref=db.backref('categoria_inversion', lazy=True))

class Medios_de_pago(db.Model):
    __tablename__ = 'medios_de_pago'

    medio_pago_id = db.Column(db.Integer, autoincrement=True ,primary_key=True)
    medio_pago = db.Column(db.Text, nullable=False)

    def __init__(self, medio_pago):
        self.medio_pago = medio_pago

    def __repr__(self):
        return f'{self.medio_pago_id, self.medio_pago}'
    
    def to_dict(self):
        return {
            'medio_pago_id': self.medio_pago_id,
            'medio_pago': self.medio_pago
        }

class Historical_money(db.Model):
    __tablename__ = 'historical_money'

    historico_id = db.Column(db.Integer, autoincrement=True ,primary_key=True)
    fecha = fecha = db.Column(db.DateTime, nullable=False)
    patrimonio = db.Column(db.Integer, nullable=False)
    liquidez = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __init__(self, fecha, patrimonio, liquidez, description):
        self.fecha = fecha
        self.patrimonio = patrimonio
        self.liquidez = liquidez
        self.description = description

    def __repr__(self):
        return f'{self.fecha, self.patrimonio, self.liquidez, self.description}'
    
    def to_dict(self):
        return {
            'fecha': self.fecha,
            'patrimonio': self.patrimonio,
            'liquidez': self.liquidez,
            'description': self.description
        }

class Categoria_ingreso(db.Model):
    
        __tablename__ = 'categoria_ingreso'
    
        categoria_ingreso_id = db.Column(db.Integer, autoincrement=True ,primary_key=True)
        categoria_ingreso = db.Column(db.Text, nullable=False)
    
        def __init__(self, categoria_ingreso):
            self.categoria_ingreso = categoria_ingreso
        
        def __repr__(self):
            return f'{self.categoria_ingreso_id, self.categoria_ingreso}'
        
        def to_dict(self):
            return {
                'categoria_ingreso_id': self.categoria_ingreso_id,
                'categoria_ingreso': self.categoria_ingreso
            }
        
class Ingresos(db.Model):
    __tablename__ = 'ingresos'

    ingreso_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    monto = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.Date(), nullable=False)
    categoria = db.Column(db.Integer, db.ForeignKey(Categoria_ingreso.categoria_ingreso_id), nullable=False)
    hash_formato = db.Column(db.Text, nullable=True)
    id_df_formato = db.Column(db.Integer, nullable=True)
    
    # Relaciones
    categoria_rel = db.relationship('Categoria_ingreso', backref=db.backref('ingresos', lazy=True))
    
    def __init__(self, description, monto, fecha, categoria, hash_formato, id_df_formato):
        self.description = description
        self.monto = monto
        self.fecha = fecha
        self.categoria = categoria
        self.hash_formato = hash_formato
        self.id_df_formato = id_df_formato
    
    def __repr__(self):
        return f'{self.description, self.monto, self.fecha, self.categoria, self.hash_formato, self.id_df_formato}'
    
    def to_dict(self):
        return {
            'description': self.description,
            'monto': self.monto,
            'fecha': self.fecha,
            'categoria': self.categoria,
            'hash_formato': self.hash_formato,
            'id_df_formato': self.id_df_formato
        }