from flask import Blueprint

investments = Blueprint(
        'investments',
        __name__,
        url_prefix='/investments',
        template_folder='templates',
        static_folder='static',
        # static_url_path='./static'
)

from . import routes