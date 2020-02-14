from flask import Flask
from flask_redis import FlaskRedis

from App.adminviews import init_admin
from App.biliviews import init_bili
from App.ext import init_ext
from App.settings import envs
from App.models import User, Userlog, Tag, Video, Preview, Comment, Videocol, Auth, Role, Admin, Adminlog, Oplog, \
    Videoup


def create_app(env):
    app = Flask(__name__)
    # 初始化配置
    app.config.from_object(envs.get(env))
    # 初始化第三方
    init_ext(app)
    # 初始化路由
    User()
    Userlog()
    Tag()
    Video()
    Preview()
    Comment()
    Videocol()
    Auth()
    Role()
    Admin()
    Adminlog()
    Oplog()
    Videoup()
    init_bili(app)
    init_admin(app)
    return app