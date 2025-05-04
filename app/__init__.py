from .extensions import db 
from flask_bootstrap import Bootstrap4
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from credentials import *
from .extensions import db, limiter, login_manager
from flask import Flask, redirect, request
from flask_talisman import Talisman
import datetime
from flask_security import Security, SQLAlchemyUserDatastore
from .models import Users, Role
migrate = Migrate()

# Se especifican los recursos CDN que tendran acceso a nuestra aplicación
# en esto caso bootstrapcdn
csp = {
    'default-src': [
        '\'self\'',
        'cdnjs.cloudflare.com',
        'stackpath.bootstrapcdn.com',
    ],
    'font-src': [
        '\'self\'',
        'fonts.googleapis.com', 
        'fonts.gstatic.com',
    ],
    'style-src': [  
        '\'self\'',
        'fonts.googleapis.com', 
        'fonts.gstatic.com',
        'cdnjs.cloudflare.com',
        'stackpath.bootstrapcdn.com',
        'cdn.datatables.net',  # Asegúrate de que esta URL coincide exactamente con la URL desde donde cargas los estilos de DataTables
        '\'unsafe-inline\'',  # Permite estilos en línea
    ],
    'img-src': [  # Añadir esta línea para permitir imágenes
        '\'self\'',
        'cdn.datatables.net',  # Permite imágenes desde DataTables
    ],
    'script-src': [  
        '\'self\'',
        'cdnjs.cloudflare.com',
        'stackpath.bootstrapcdn.com',
        'unpkg.com',  # Asegúrate de que esta URL coincide exactamente con la URL desde donde cargas cualquier script desde unpkg
        'cdn.jsdelivr.net',
        'code.jquery.com',  # Permite cargar jQuery desde su CDN
        '\'unsafe-inline\'',  # Permite scripts en línea
        'cdn.datatables.net',  # Asegúrate de que esta URL coincide exactamente con la URL desde donde cargas los scripts de DataTables
    ]
}

def create_app():
    #creamos la app
    app = Flask(__name__)
    
    #Asignamos la base de datos a la app
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    #Proteccián cfr
    app.secret_key = secret_key #llave secreta
    app.config['SECURITY_ENABLED'] = SECURITY_ENABLED
    app.config["SECURITY_CSRF_COOKIE_NAME"] = SECURITY_CSRF_COOKIE_NAME #nombre de la cookie de seguridad
    app.config["WTF_CSRF_TIME_LIMIT"] = WTF_CSRF_TIME_LIMIT #Tiempo de validez de la cookie
    app.config["SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS"] = SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS #Endponts sin seguridad
    app.config["SECURITY_CSRF_PROTECT_MECHANISMS"] = SECURITY_CSRF_PROTECT_MECHANISMS
    app.config["SECURITY_FRESHNESS_GRACE_PERIOD"] = SECURITY_FRESHNESS_GRACE_PERIOD  # Periodo de gracia de seguridad
    app.config["SECURITY_ANONYMOUS_USER_DISABLED"] = SECURITY_ANONYMOUS_USER_DISABLED  # Permitir usuarios anónimos
    app.config["WTF_CSRF_CHECK_DEFAULT"] = WTF_CSRF_CHECK_DEFAULT  # Requerido cuando CSRF_PROTECT_MECHANISMS está configurado
    
    # Flask-Security configuration - more complete setup
    app.config["SECURITY_URL_PREFIX"] = None  # Don't use a prefix for security routes
    app.config["SECURITY_LOGIN_USER_TEMPLATE"] = None  # Don't use security's login template
    app.config["SECURITY_REGISTER_USER_TEMPLATE"] = None  # Don't use security's register template
    app.config["SECURITY_REGISTERABLE"] = False  # Disable Flask-Security registration
    app.config["SECURITY_CHANGEABLE"] = False  # Disable password change
    app.config["SECURITY_RECOVERABLE"] = False  # Disable password recovery
    app.config["SECURITY_POST_LOGIN_VIEW"] = "/resume/"  # Where to redirect after login
    app.config["SECURITY_POST_LOGOUT_VIEW"] = "/"  # Where to redirect after logout
    app.config["SECURITY_LOGIN_URL"] = "/"
    app.config["SECURITY_SEND_REGISTER_EMAIL"] = False  # Don't send registration emails
    app.config["SECURITY_CONFIRMABLE"] = False  # Don't require email confirmation
    app.config["SECURITY_DEFAULT_REMEMBER_ME"] = True  # Remember users by default
    
    # Override security endpoints to use your blueprint routes
    app.config["SECURITY_LOGIN_URL"] = "/"
    app.config["SECURITY_LOGOUT_URL"] = "/logout"
    app.config["SECURITY_REGISTER_URL"] = "/signup"
    
    # Set custom endpoints to fix redirection issues
    app.config["SECURITY_AUTH_URL"] = "/"  # Use your login page for auth
    app.config["SECURITY_REDIRECT_BEHAVIOR"] = "spa"  # Use SPA redirect handling
    app.config["SECURITY_REDIRECT_HOST"] = "127.0.0.1:616"  # Set your host
    
    # Disable CSRF protection specifically for the /login endpoint, since your form handles it
    app.config["SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS"] = True
    app.config["SECURITY_CSRF_PROTECT_MECHANISMS"] = ["basic", "session", "token"]
    
    csrf = CSRFProtect(app)
    
    # Habilitamos el control de sesiones
    login_manager.init_app(app)
    login_manager.session_protection = "strong"  # Add session protection
    
    # Directly set the unauthorized callback to avoid Flask-Security's handler
    @login_manager.unauthorized_handler
    def unauthorized_callback():
        next_url = request.full_path
        return redirect(f'/?next={next_url}')

    #traemos el limitador de extensions y la aplicamos a la aplicación
    limiter.init_app(app)
    # Initialize bootstrap
    bootstrap = Bootstrap4(app)

    #Forzamos encriptación HTTPS
    talisman = Talisman(app, content_security_policy=csp)
    # Evitar que so puedan poner frames sobre la aplicación
    talisman.frame_options = 'sameorigin'

    db.init_app(app)
    migrate.init_app(app, db)
    
    # Update session cookie configuration to work in local development
    app.config.update(
        SESSION_COOKIE_SECURE=False,  # Changed to False for local testing
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=datetime.timedelta(days=1)
    )

    # Initialize Flask-Security but disable its views
    from flask_security.utils import url_for_security as original_url_for_security
    from flask import url_for
    
    # Create a patched version of url_for_security that maps security endpoints to our actual routes
    def patched_url_for_security(endpoint, **values):
        # Map security endpoints to our blueprint routes
        if endpoint == 'login' or endpoint == 'security.login':
            return url_for('login.login_app', **values)  # Use our login route
        elif endpoint == 'logout':
            return url_for('login.logout', **values)     # Use our logout route
        elif endpoint == 'register':
            return url_for('login.register_app', **values)  # Use our register route
        
        # For any other security endpoints, don't try the original function
        # Just default to our login page
        return url_for('login.login_app', **values)
    
    # Create the security object with customizations
    user_datastore = SQLAlchemyUserDatastore(db, Users, Role)
    security = Security(app, user_datastore, register_blueprint=False)  # Don't register Flask-Security's blueprint
    
    # Replace the original url_for_security function with our patched version
    import flask_security.utils
    flask_security.utils.url_for_security = patched_url_for_security
    
    # Override Flask-Security's auth_required decorator to use Flask-Login
    import flask_security.decorators
    
    # Completely replace Flask-Security's auth_required with Flask-Login's login_required
    def new_auth_required(*args, **kwargs):
        return login_required
    
    flask_security.decorators.auth_required = new_auth_required
    
    # Override the default_unauthn_handler to avoid using url_for_security
    def new_default_unauthn_handler():
        next_url = request.full_path
        return redirect(f'/?next={next_url}')
    
    flask_security.decorators.default_unauthn_handler = new_default_unauthn_handler

    app.permanent_session_lifetime = datetime.timedelta(days=1)
    
    from app.blueprints.login import login
    app.register_blueprint(login)

    from app.blueprints.resume import resume
    app.register_blueprint(resume)

    from app.blueprints.wastes import wastes
    app.register_blueprint(wastes)

    from app.blueprints.investments import investments
    app.register_blueprint(investments)

    from app.blueprints.valoracion import valoracion
    app.register_blueprint(valoracion)

    # Add direct route handlers for security redirects
    @app.route('/login', methods=['GET'])
    def login_redirect():
        """Handle redirects to /login by sending to root / with next parameter"""
        # Get query string parameters
        next_url = request.args.get('next', '/resume/')
        # Redirect to root with next parameter
        return redirect(f'/?next={next_url}')
        
    @app.route('/security/login', methods=['GET'])
    def security_login_redirect():
        """Handle redirects to /security/login by sending to root /"""
        # Get query string parameters
        next_url = request.args.get('next', '/resume/')
        # Redirect to root with next parameter
        return redirect(f'/?next={next_url}')
    
    # Add a direct route for the security.login endpoint
    @app.route('/login', endpoint='security.login')
    def security_login():
        """Handle the security.login endpoint to prevent BuildError"""
        next_url = request.args.get('next', '/resume/')
        return redirect(f'/?next={next_url}')

    return app