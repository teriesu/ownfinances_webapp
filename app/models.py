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
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=True)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


    def __init__(self, user, email, password, roles=None, active=True, fs_uniquifier=None):
        self.user=user
        self.email = email
        self.password = password
        self.active = active
        self.fs_uniquifier = fs_uniquifier
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
        # Use fs_uniquifier as unique identifier for the user as required by Flask-Security
        return str(self.fs_uniquifier)
    
    def is_authenticated(self):
        # Always return True for logged-in users
        return True
    
    def is_anonymous(self):
        # Always return False for logged-in users
        return False

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

class Medios_de_pago(db.Model):
    __tablename__ = 'medios_de_pago'

    medio_pago_id = db.Column(db.Integer, autoincrement=True ,primary_key=True)
    medio_pago = db.Column(db.Text, nullable=False)

    def __init__(self, medio_pago, cuenta_origen_id=None):
        self.medio_pago = medio_pago
        self.cuenta_origen_id = cuenta_origen_id

    def __repr__(self):
        return f'{self.medio_pago_id, self.medio_pago}'
    
    def to_dict(self):
        return {
            'medio_pago_id': self.medio_pago_id,
            'medio_pago': self.medio_pago,
            'cuenta_origen_id': self.cuenta_origen_id
        }
    
class Medios_pago_cuentas(db.Model):
    __tablename__ = 'medios_pago_cuentas'

    medio_pago_cuenta_id = db.Column(db.Integer, autoincrement=True ,primary_key=True)
    medio_pago_id = db.Column(db.Integer, db.ForeignKey(Medios_de_pago.medio_pago_id), nullable=False)
    cuenta_id = db.Column(db.Integer, db.ForeignKey('cuentas.cuenta_id'), nullable=False)

    # Relaciones
    medio_pago_rel = db.relationship('Medios_de_pago', backref=db.backref('medios_pago_cuentas', lazy=True))
    cuenta_rel = db.relationship('Cuentas', backref=db.backref('medios_pago_cuentas', lazy=True))

    def __init__(self, medio_pago_id, cuenta_id):
        self.medio_pago_id = medio_pago_id
        self.cuenta_id = cuenta_id

    def __repr__(self):
        return f'{self.medio_pago_cuenta_id, self.medio_pago_id, self.cuenta_id}'
    
    def to_dict(self):
        return {
            'medio_pago_cuenta_id': self.medio_pago_cuenta_id,
            'medio_pago_id': self.medio_pago_id,
            'cuenta_id': self.cuenta_id
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
    
class Divisa(db.Model):
    __tablename__ = 'divisas'

    divisa_id = db.Column(db.Integer, autoincrement=True ,primary_key=True)
    divisa = db.Column(db.Text, nullable=False)
    simbolo = db.Column(db.String, nullable=False)
    abreviacion = db.Column(db.Text, nullable=False)

    def __init__(self, divisa, simbolo, abreviacion):
        self.divisa = divisa
        self.simbolo = simbolo
        self.abreviacion = abreviacion

    def __repr__(self):
        return f'{self.divisa_id, self.divisa, self.simbolo, self.abreviacion}'

    def to_dict(self):
        return {
            'divisa_id': self.divisa_id,
            'divisa': self.divisa,
            'simbolo': self.simbolo,
            'abreviacion': self.abreviacion
        }

class Gastos(db.Model):

    __tablename__ = 'gastos'

    gasto_id = db.Column(db.Integer, autoincrement=True ,primary_key=True)
    description = db.Column(db.Text, nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.Date(), nullable=False)
    categoria = db.Column(db.Integer, db.ForeignKey(CategoriaGasto.categoria_id), nullable=False)
    hash_formato = db.Column(db.Text, nullable=True)
    id_df_formato = db.Column(db.Integer, nullable=True)
    id_patrimonio = db.Column(db.Integer, db.ForeignKey(Bienes.bien_id), nullable=True)
    essential = db.Column(db.Boolean, nullable=False)
    divisa = db.Column(db.Integer, db.ForeignKey(Divisa.divisa_id), nullable=True)
    medio_pago_id = db.Column(db.Integer, db.ForeignKey(Medios_de_pago.medio_pago_id), nullable=True)


    #Relaciones
    categoria_rel = db.relationship('CategoriaGasto', backref=db.backref('categoria_gasto', lazy=True))
    bien_rel = db.relationship('Bienes', backref=db.backref('gastos_bienes', lazy=True))
    divisa_rel = db.relationship('Divisa', backref=db.backref('gastos_divisa', lazy=True))
    medio_pago_rel = db.relationship('Medios_de_pago', backref=db.backref('gastos_medio_pago', lazy=True))

    def __init__(self, description, monto, fecha, categoria, hash_formato, id_df_formato, id_patrimonio, essential, divisa, medio_pago_id):
        self.description = description
        self.monto = monto
        self.fecha = fecha
        self.categoria = categoria
        self.hash_formato = hash_formato
        self.id_df_formato = id_df_formato
        self.id_patrimonio = id_patrimonio
        self.essential = essential
        self.divisa = divisa
        self.medio_pago_id = medio_pago_id

    def __repr__(self):
        return f'{self.description, self.monto, self.fecha, self.categoria, self.hash_formato, self.id_df_formato, self.id_patrimonio, self.essential, self.divisa, self.medio_pago_id}'

    def to_dict(self):
        return {
            'description': self.description,
            'monto': self.monto,
            'fecha': self.fecha,
            'categoria': self.categoria,
            'hash_formato': self.hash_formato,
            'id_df_formato': self.id_df_formato,
            'id_patrimonio': self.id_patrimonio,
            'essential': self.essential,
            'divisa': self.divisa,
            'medio_pago_id': self.medio_pago_id
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

class PlataformasInversion(db.Model):
    __tablename__ = 'plataformas_inversion'

    plataforma_id = db.Column(db.Integer, autoincrement=True ,primary_key=True)
    plataforma = db.Column(db.Text, nullable=False)

    def __init__(self, plataforma):
        self.plataforma = plataforma

    def __repr__(self):
        return f'{self.plataforma_id, self.plataforma}'
    
    def to_dict(self):
        return {
            'plataforma_id': self.plataforma_id,
            'plataforma': self.plataforma
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
    cerrada = db.Column(db.Boolean, nullable=True)

    #Relaciones
    categoria_rel = db.relationship('CategoriaInversion', backref=db.backref('categoria_inversion', lazy=True))

    def __init__(self, description, monto, rentab_esperada, fecha, categoria, hash_formato, id_df_formato, cerrada = False):
        self.description = description
        self.monto = monto
        self.rentab_esperada = rentab_esperada
        self.fecha = fecha
        self.categoria = categoria
        self.hash_formato = hash_formato
        self.id_df_formato = id_df_formato
        self.cerrada = cerrada
    
    def __repr__(self):
        return f'{self.description, self.monto, self.rentab_esperada, self.fecha, self.categoria, self.hash_formato, self.id_df_formato}'
    
    def to_dict(self):
        return {
            'description': self.description,
            'monto': self.monto,
            'rentab_esperada': self.rentab_esperada,
            'fecha': self.fecha,
            'categoria': self.categoria,
            'hash_formato': self.hash_formato,
            'id_df_formato': self.id_df_formato
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
    
class Cuentas(db.Model):
    __tablename__ = 'cuentas'

    cuenta_id = db.Column(db.Integer, autoincrement=True ,primary_key=True)
    institucion_financiera = db.Column(db.Text, nullable=False)
    nombre_cuenta = db.Column(db.Text, nullable=False)
    divisa = db.Column(db.Integer, db.ForeignKey(Divisa.divisa_id), nullable=False)

    #Relaciones
    divisa_rel = db.relationship('Divisa', backref=db.backref('cuentas_divisa', lazy=True))

    def __init__(self, institucion_financiera, nombre_cuenta, divisa):
        self.institucion_financiera = institucion_financiera
        self.nombre_cuenta = nombre_cuenta
        self.divisa = divisa

    def __repr__(self):
        return f'{self.cuenta_id, self.institucion_financiera, self.nombre_cuenta, self.divisa}'

    def to_dict(self):
        return {
            'cuenta_id': self.cuenta_id,
            'institucion_financiera': self.institucion_financiera,
            'nombre_cuenta': self.nombre_cuenta,
            'divisa': self.divisa
        }
    
class SaldoCuenta(db.Model):
    __tablename__ = 'saldo_cuenta'

    saldo_id = db.Column(db.Integer, autoincrement=True ,primary_key=True)
    cuenta_id = db.Column(db.Integer, db.ForeignKey(Cuentas.cuenta_id), nullable=False)
    saldo = db.Column(db.Float, nullable=False)
    fecha_movimiento = db.Column(db.Date(), nullable=False)
    fecha_registro = db.Column(db.DateTime, nullable=False)
    hash_formato = db.Column(db.Text, nullable=True)
    id_df_formato = db.Column(db.Integer, nullable=True)
    descripcion = db.Column(db.Text, nullable=True)

    #Relaciones
    cuenta_rel = db.relationship('Cuentas', backref=db.backref('saldos_cuenta', lazy=True))

    def __init__(self, cuenta_id, saldo, fecha_movimiento, hash_formato=None, id_df_formato=None, descripcion=None):
        self.cuenta_id = cuenta_id
        self.saldo = saldo
        self.fecha_movimiento = fecha_movimiento
        self.fecha_registro = datetime.datetime.now()
        self.hash_formato = hash_formato
        self.id_df_formato = id_df_formato
        self.descripcion = descripcion

    def __repr__(self):
        return f'{self.saldo_id, self.cuenta_id, self.saldo, self.fecha_movimiento}'

    def to_dict(self):
        return {
            'saldo_id': self.saldo_id,
            'cuenta_id': self.cuenta_id,
            'saldo': self.saldo,
            'fecha_movimiento': self.fecha_movimiento,
            'fecha_registro': self.fecha_registro,
            'hash_formato': self.hash_formato,
            'id_df_formato': self.id_df_formato,
            'descripcion': self.descripcion
        }

class Transferencias(db.Model):
    __tablename__ = 'transferencias'

    transferencia_id = db.Column(db.Integer, autoincrement=True ,primary_key=True)
    cuenta_origen = db.Column(db.Integer, db.ForeignKey(Cuentas.cuenta_id), nullable=False)
    cuenta_destino = db.Column(db.Integer, db.ForeignKey(Cuentas.cuenta_id), nullable=False)
    monto_enviado = db.Column(db.Float, nullable=False)
    divisa_origen = db.Column(db.Integer, db.ForeignKey(Divisa.divisa_id), nullable=False)
    monto_recibido = db.Column(db.Float, nullable=False)
    divisa_destino = db.Column(db.Integer, db.ForeignKey(Divisa.divisa_id), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    descripcion = db.Column(db.Text, nullable=True)

    #Relaciones
    cuenta_origen_rel = db.relationship('Cuentas', foreign_keys=[cuenta_origen], backref=db.backref('transferencias_origen', lazy=True))
    cuenta_destino_rel = db.relationship('Cuentas', foreign_keys=[cuenta_destino], backref=db.backref('transferencias_destino', lazy=True))
    divisa_origen_rel = db.relationship('Divisa', foreign_keys=[divisa_origen], backref=db.backref('transferencias_divisa_origen', lazy=True))
    divisa_destino_rel = db.relationship('Divisa', foreign_keys=[divisa_destino], backref=db.backref('transferencias_divisa_destino', lazy=True))

    def __init__(self, cuenta_origen, cuenta_destino, monto_enviado, divisa_origen, monto_recibido, divisa_destino, fecha, descripcion):
        self.cuenta_origen = cuenta_origen
        self.cuenta_destino = cuenta_destino
        self.monto_enviado = monto_enviado
        self.divisa_origen = divisa_origen
        self.monto_recibido = monto_recibido
        self.divisa_destino = divisa_destino
        self.fecha = fecha
        self.descripcion = descripcion

    def __repr__(self):
        return f'{self.transferencia_id, self.cuenta_origen, self.cuenta_destino, self.monto_enviado, self.divisa_origen, self.monto_recibido, self.divisa_destino, self.fecha, self.descripcion}'
    
    def to_dict(self):
        return {
            'transferencia_id': self.transferencia_id,
            'cuenta_origen': self.cuenta_origen,
            'cuenta_destino': self.cuenta_destino,
            'monto_enviado': self.monto_enviado,
            'divisa_origen': self.divisa_origen,
            'monto_recibido': self.monto_recibido,
            'divisa_destino': self.divisa_destino,
            'fecha': self.fecha,
            'descripcion': self.descripcion
        }
