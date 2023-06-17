from .extensions import db 
from flask_bootstrap import Bootstrap4
from flask_migrate import Migrate
from credentials import *
from .extensions import db 
from flask import Flask

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize bootstrap
    bootstrap = Bootstrap4(app)
    app.secret_key = 'Alco'
    
    from app.blueprints.login import login
    app.register_blueprint(login)

    return app