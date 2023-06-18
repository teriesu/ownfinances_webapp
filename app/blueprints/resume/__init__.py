from flask import Blueprint

resume = Blueprint(
        'resume',
        __name__,
        url_prefix='/resume',
        template_folder='templates',
        static_folder='static',
        # static_url_path='./static'
)

from . import routes