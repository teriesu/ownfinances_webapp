from .extensions import db 
from flask_bootstrap import Bootstrap4
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from credentials import *
from .extensions import db, limiter, login_manager
from flask import Flask
from flask_talisman import Talisman
import datetime
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
    csrf = CSRFProtect(app)
    
    # Habilitamos el control de sesiones
    login_manager.init_app(app)

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
    
    # Configura la cookie de sesión para que solo se envíe a través de HTTPS
    # 
    app.config.update(
        SESSION_COOKIE_SECURE=True,
    )

    # Marca las cookies de sesión como HttpOnly, 
    # evita que las cookies de sesión sean accesibles a través de JavaScript en el navegador
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
    )

    # Esta es una opción de las cookies que puede ayudar a proteger contra los ataques de tipo CSRF (Cross-Site Request Forgery)
    # Puedes configurar la opción SESSION_COOKIE_SAMESITE de Flask en 'Strict' o 'Lax' 
    app.config.update(
        SESSION_COOKIE_SAMESITE='Lax',
    )

    # from flask_security import Security, SQLAlchemyUserDatastore
    # user_datastore = SQLAlchemyUserDatastore(db, Users, Role)
    # security = Security(app, user_datastore)

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

    return app