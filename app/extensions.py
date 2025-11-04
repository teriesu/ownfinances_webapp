#Crear la base de datos de tipo SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()   

#Crear el engine para consultas en la base de datos
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from credentials import *
from .init_utils import get_windows_host_ip_from_wsl
import platform

host = HOST

if "microsoft" in platform.uname().release.lower():
    wsl_ip = get_windows_host_ip_from_wsl()
    if wsl_ip:
        host = wsl_ip

engine = create_engine(f'postgresql+psycopg2://{USERNAME}:{PASSWORD}@{host}:{PORT}/{DATABASE}')
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
from flask_login import current_user
from flask import redirect, flash, jsonify

def role_required(roles):
    """
    Decorator for views that require specific roles.
    Add @role_required('role_name') or @role_required(['role_name1', 'role_name2'])
    """
    # Convert single role to list for consistent handling
    if isinstance(roles, str):
        roles = [roles]
        
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # First check if user is logged in
            if not current_user.is_authenticated:
                flash('You need to login first.')
                return redirect('/')
                
            # Check if user has any of the required roles
            user_has_role = False
            for role in current_user.roles:
                if role.name in roles:
                    user_has_role = True
                    break
                    
            if not user_has_role:
                allowed_roles = ', '.join(roles)
                flash(f'You do not have permission to access this page. Only {allowed_roles} roles are allowed.')
                return redirect('/')
                
            # User has necessary role, proceed with the view
            return f(*args, **kwargs)
        return decorated_function
    return decorator

from app.gdrive_management import Gdrive
gdrive = Gdrive()