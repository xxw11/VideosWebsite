def init_admin(app):
    app.register_blueprint(admin,)
from flask import Blueprint

admin = Blueprint('admin', __name__,url_prefix='/admin')

import App.adminviews.views
