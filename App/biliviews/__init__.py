def init_bili(app):
    @app.errorhandler(404)
    def hello(e):
        return render_template('error/404.html')
    app.register_blueprint(bili)

from flask import Blueprint, render_template

bili = Blueprint('bili', __name__)
import App.biliviews.views
