#Crear la base de datos de tipo SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()   

#Crear el engine para consultas en la base de datos
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from credentials import *
engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')
Session = sessionmaker(bind=engine)

# Creamos el limitador de solicitudes por endpoint
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)

# Para configurar un almacenamiento diferente, 
# puedes hacerlo al instanciar el objeto Limiter. 
# Por ejemplo, para utilizar Redis como almacenamiento, 
# puedes hacerlo de la siguiente manera:

# limiter = Limiter(key_func=get_remote_address, storage_uri='redis://localhost:6379')

# Inicializar el objeto LoginManager
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.login_view = '/'  # Set the login route
login_manager.login_message = "You must sign in to view this resource."
login_manager.login_message_category = "info"

from functools import wraps
from flask_login import LoginManager, current_user
from flask import redirect, flash
from app.models import Users
def role_required(roles):
    if isinstance(roles, str):
        roles = [roles]

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('You need to login first.')
                return redirect('/')
            elif not any(role.name in roles for role in current_user.roles):
                allowed_roles = ', '.join(roles)
                flash(f'You do not have permission to access this page. Only {allowed_roles} roles are allowed.')
                return redirect('/')  # redirect to a suitable error/access denied page
            return f(*args, **kwargs)
        return decorated_function
    return decorator

from app.gdrive_management import Gdrive
gdrive = Gdrive()