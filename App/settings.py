import os


def get_db_uri(dbinfo):
    engine = dbinfo.get("ENGINE")
    driver = dbinfo.get('DRIVER')
    user = dbinfo.get('USER')
    password = dbinfo.get("PASSWORD")
    host = dbinfo.get("HOST")
    port = dbinfo.get('PORT')
    name = dbinfo.get('NAME')
    return "{}+{}://{}:{}@{}:{}/{}".format(engine, driver, user, password, host, port, name)


class Config:
    TESTING = False

    DEBUG = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = '1afd3cb7304c429998716ea76acb1c38'

    SESSION_TYPE = 'redis'

    UP_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/videos/")

    FC_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/usricons/")

    REDIS_URL = "redis://:@localhost:6379/0"



class DevelopConfig(Config):
    DEBUG = True

    dbinfo = {
        'ENGINE': 'mysql',
        'DRIVER': 'pymysql',
        'USER': 'root',
        'PASSWORD': 'rock1204',
        'HOST': 'localhost',
        'PORT': '3305',
        'NAME': 'bili'
    }

    SQLALCHEMY_DATABASE_URI = get_db_uri(dbinfo)


class ProductConfig(Config):
    dbinfo = {
        'ENGINE': 'mysql',
        'DRIVER': 'pymysql',
        'USER': 'root',
        'PASSWORD': 'rock1204',
        'HOST': 'localhost',
        'PORT': '3305',
        'NAME': 'bili'
    }

    SQLALCHEMY_DATABASE_URI = get_db_uri(dbinfo)


envs = {
    "develop": DevelopConfig,
    "product": ProductConfig,
    "default": DevelopConfig,
}
