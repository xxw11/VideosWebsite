from datetime import datetime

from App.ext import db


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(128))
    email = db.Column(db.String(128), unique=True)
    phone = db.Column(db.String(16), unique=True)
    mood = db.Column(db.Text)  # 想说的话，签名
    icon = db.Column(db.String(255), unique=True)  # 头像
    addtime = db.Column(db.DateTime, index=True, default=datetime.now())
    uuid = db.Column(db.String(64))
    userlogs = db.relationship('Userlog', backref='user')
    videos = db.relationship('Video', backref='user')
    comments = db.relationship('Comment', backref='user')
    video_cols = db.relationship('Videocol', backref='user')

    def __repr__(self):
        return "<User %r>" % self.name
    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password, pwd)
        # return pwd == self.password
# 会员登录日志
class Userlog(db.Model):
    __tablename__ = 'userlog'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ip = db.Column(db.String(100))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now())

    def __repr__(self):
        return "<Userlog %r>" % self.id


# 标签
class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)  # 标题
    addtime = db.Column(db.DateTime, index=True, default=datetime.now())  # 添加时间
    videos = db.relationship('Video', backref='tag')

    def __repr__(self):
        return "<Tag %r>" % self.name



# 视频
class Video(db.Model):
    __tablename__ = 'video'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True)
    url = db.Column(db.String(255), unique=True)  # 地址
    info = db.Column(db.Text)  # 简介
    logo = db.Column(db.String(255), unique=True)  # 封面
    star = db.Column(db.SmallInteger)  # 星级评分
    playnum = db.Column(db.BigInteger)  # 播放量
    commentnum = db.Column(db.BigInteger)  # 评论量
    col_num=db.Column(db.Integer,default=0)  #收藏量
    up_num=db.Column(db.Integer,default=0)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))  # 所属标签
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户
    comments = db.relationship('Comment', backref='video')  # 评论
    video_cols = db.relationship('Videocol', backref='video')  # 收藏
    video_ups = db.relationship('Videoup', backref='video')#点赞
    release_time = db.Column(db.Date)  # 上映时间
    area = db.Column(db.String(255))  # 上映地区
    length = db.Column(db.String(100))  # 播放时长
    addtime = db.Column(db.DateTime, index=True, default=datetime.now())  # 添加时间

    def __repr__(self):
        return "<Video %r>" % self.title

# 上映预告
class Preview(db.Model):
    __tablename__ = "preview"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True)
    logo = db.Column(db.String(255), unique=True)  # 封面
    addtime = db.Column(db.DateTime, index=True, default=datetime.now())

    def __repr__(self):
        return "<Preview %r>" % self.title


# 评论
class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now())

    def __repr__(self):
        return "<Comment %r>" % self.id


# 视频收藏
class Videocol(db.Model):
    __tablename__ = "videocol"
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now())

    def __repr__(self):
        return "<Videocol %r>" % self.id

# 视频点赞
class Videoup(db.Model):
    __tablename__ = "videoup"
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now())

    def __repr__(self):
        return "<Videocol %r>" % self.id


class Auth(db.Model):
    __tablename__ = "auth"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(255), unique=True)  # 名称
    url = db.Column(db.String(255), unique=True)  # 地址
    addtime = db.Column(db.DateTime, index=True, default=datetime.now())

    def __repr__(self):
        return "<Auth %r>" % self.id


# 角色
class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)  # 名称
    auths = db.Column(db.String(600))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now())
    admins = db.relationship("Admin", backref='role')

    def __repr__(self):
        return "<Role %r>" % self.name


# 管理员
class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)  # 管理员账号
    password = db.Column(db.String(128))  # 管理员密码
    is_super = db.Column(db.SmallInteger)  # 是否是超级管理员 0为超级管理员
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))  # 所属角色
    addtime = db.Column(db.DateTime, index=True, default=datetime.now())
    adminlogs = db.relationship("Adminlog", backref='admin')
    Oplogs = db.relationship("Oplog", backref='admin')

    def __repr__(self):
        return "<Admin %r>" % self.name

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password, pwd)
        # return pwd == self.password


# 管理员登录日志
class Adminlog(db.Model):
    __tablename__ = 'adminlog'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    ip = db.Column(db.String(100))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now())

    def __repr__(self):
        return "<Adminlog %r>" % self.id


# 操作日志
class Oplog(db.Model):
    __tablename__ = 'oplog'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    ip = db.Column(db.String(100))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now())
    reason = db.Column(db.String(600))  # 操作原因

    def __repr__(self):
        return "<Oplog %r>" % self.id
