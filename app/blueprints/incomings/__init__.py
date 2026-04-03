from flask import Blueprint

incomings = Blueprint(
        'incomings',
        __name__,
        url_prefix='/incomings',
        template_folder='templates',
        static_folder='static',
        # static_url_path='./static'
)

from . import routes