
from flask_migrate import Migrate
from flask_redis import FlaskRedis

from flask_sqlalchemy import SQLAlchemy



db = SQLAlchemy()
migrate = Migrate()
rd = FlaskRedis()

def init_ext(app):
    db.init_app(app)
    migrate.init_app(app, db)
    rd.init_app(app)



