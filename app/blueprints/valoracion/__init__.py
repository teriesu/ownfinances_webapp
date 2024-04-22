from flask import Blueprint

valoracion = Blueprint(
        'valoracion',
        __name__,
        url_prefix='/valoracion',
        template_folder='templates',
        static_folder='static',
        # static_url_path='./static'
)

from . import routes