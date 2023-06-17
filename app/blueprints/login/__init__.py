from flask import Blueprint

login = Blueprint(
        'login',
        __name__,
        url_prefix='/',
        template_folder='templates',
        static_folder='static',
        # static_url_path='./static'
)

from . import routes