from flask import Blueprint

wastes = Blueprint(
        'wastes',
        __name__,
        url_prefix='/wastes',
        template_folder='templates',
        static_folder='static',
        # static_url_path='./static'
)

from . import routes