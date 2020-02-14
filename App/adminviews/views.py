import datetime
import os
import uuid

from functools import wraps

from flask import render_template, redirect, flash, session, request, url_for
from werkzeug.utils import secure_filename

from . import admin
from .forms import LoginForm, TagForm, VideoForm, PwdForm
from App.models import Admin, Tag, Video, User, Comment
from ..ext import db


# 登录装饰器，访问控制
def admin_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('admin') is None:
            return redirect(url_for('admin.login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


# 修改上传文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex + fileinfo[-1]
    return filename


@admin.route("/")
@admin_login_req
def index():
    return render_template('admin/index.html')


@admin.route("/login/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=data["account"]).first()

        if not admin.check_pwd(data["pwd"]):
            flash("密码错误")
            return redirect(url_for('admin.login'))
        session['admin'] = data['account']
        return redirect(request.args.get("next") or url_for("admin.index"))
    return render_template('admin/login.html', form=form)


@admin.route("/logout/")
@admin_login_req
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin.login'))


@admin.route("/pwd/", methods=['GET', 'POST'])
@admin_login_req
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=session['admin']).first()
        from werkzeug import generate_password_hash
        admin.password = generate_password_hash(data['new_pwd'])
        db.session.add(admin)
        db.session.commit()
        flash('修改密码成功', 'ok')
        return redirect(url_for('admin.logout'))
    return render_template('admin/pwd.html', form=form)


# 标签列表
@admin.route("/tag/list/<int:page>")
@admin_login_req
def taglist(page):
    if page is None:
        page = 1
    page_data = Tag.query.order_by(
        Tag.id.asc()
    ).paginate(page=page, per_page=10)
    return render_template('admin/tag_list.html', page_data=page_data)


# 标签添加
@admin.route("/tag/add/", methods=['GET', 'POST'])
@admin_login_req
def tagadd():
    form = TagForm()
    if form.validate_on_submit():
        data = form.data
        tag = Tag.query.filter_by(name=data['name']).count()
        if tag == 1:
            flash('名称已经存在', 'err')
            return redirect(url_for('admin.tagadd'))
        tag = Tag(
            name=data['name']
        )
        db.session.add(tag)
        db.session.commit()
        flash('添加标签成功', 'ok')
        return redirect(url_for('admin.tagadd'))
    return render_template('admin/tag_add.html', form=form)


# 标签删除
@admin.route("/tag/del/<int:id>")
@admin_login_req
def tagdel(id):
    tag = Tag.query.filter_by(id=id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    flash('删除标签成功', 'ok')
    return redirect(url_for('admin.taglist', page=1))


# 视频列表
@admin.route("/video/list/<int:page>")
@admin_login_req
def videolist(page):
    if page is None:
        page = 1
    page_data = Video.query.join(Tag).filter(
        Tag.id == Video.tag_id
    ).order_by(
        Video.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template('admin/video_list.html', page_data=page_data)


# 添加视频
@admin.route("/video/add/", methods=['POST', 'GET'])
@admin_login_req
def videoadd():
    form = VideoForm()

    form.tag_id.choices = [(v.id, v.name) for v in Tag.query.all()]
    # if request.method =="POST":
    if form.validate_on_submit():
        data = form.data
        file_url = secure_filename(form.url.data.filename)
        file_logo = secure_filename(form.logo.data.filename)
        from manage import app
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config['UP_DIR'],)
            os.chmod(app.config['UP_DIR'],'rw')
        url = change_filename(file_url)
        logo = change_filename(file_logo)
        form.url.data.save(app.config['UP_DIR'] + url)
        form.logo.data.save(app.config['UP_DIR'] + logo)
        video = Video(
            title=data['name'],
            url=url,
            info=data['info'],
            logo=logo,
            playnum=0,
            commentnum=0,
            tag_id=data['tag_id'],
            release_time=data['release_time'] or datetime.datetime.now(),
            length=data['length'] or None,
        )
        db.session.add(video)
        db.session.commit()
        flash('添加视频成功', 'ok')
        return redirect(url_for('admin.videoadd'))
    return render_template('admin/video_add.html', form=form)


# 删除视频
@admin.route("/video/del/<int:id>")
@admin_login_req
def videodel(id):
    video = Video.query.filter_by(id=id).first_or_404()
    db.session.delete(video)
    db.session.commit()

    flash('删除视频成功', 'ok')
    return redirect(url_for('admin.videolist', page=1))


# 编辑视频
@admin.route("/video/edit/<int:id>", methods=['POST', 'GET'])
@admin_login_req
def videoedit(id):
    form = VideoForm()
    video = Video.query.get_or_404(id)
    form.tag_id.choices = [(v.id, v.name) for v in Tag.query.all()]
    form.url.validators = []
    form.logo.validators = []
    if request.method == "GET":
        form.info.data = video.info
        form.name.data = video.title
        form.tag_id.data = video.tag_id
    if form.validate_on_submit():
        data = form.data
        from manage import app
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config['UP_DIR'])
            os.chmod(app.config['UP_DIR'],'rw')
        if form.url.data.filename:
            file_url = secure_filename(form.url.data.filename)
            video.url = change_filename(file_url)
            form.url.data.save(app.config['UP_DIR'] + video.url)
        if form.logo.data.filename:
            file_logo = secure_filename(form.logo.data.filename)
            video.logo = change_filename(file_logo)
            form.logo.data.save(app.config['UP_DIR'] + video.logo)
        video_count = Video.query.filter_by(title=data['name']).count()
        if video_count == 1 and video.title != data['name']:
            flash('编辑视频失败', 'err')
            return redirect(url_for('admin.videoedit', id=video.id))
        video.title = data['name']
        video.tag_id = data['tag_id']
        video.info = data['info']
        video.length = data['length']
        video.release_time = data['release_time']
        db.session.add(video)
        db.session.commit()
        flash('编辑视频成功', 'ok')
        return redirect(url_for('admin.videoedit', id=video.id))
    return render_template('admin/video_edit.html', form=form, video=video)


@admin.route("/user/list/<int:page>")
@admin_login_req
def userlist(page):
    if page is None:
        page=1
    page_data = User.query.order_by(
        User.id.asc()
    ).paginate(page=page, per_page=10)
    return render_template('admin/user_list.html',page_data=page_data)


@admin.route("/user/view/<int:id>")
@admin_login_req
def userview(id):
    user=User.query.get(id)
    return render_template('admin/user_view.html',user=user)

@admin.route("/user/delete/<int:id>")
@admin_login_req
def userdelete(id):
    user=User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    flash('用户删除成功','ok')
    return redirect(url_for('admin.userlist',page=1))

@admin.route("/comment/list/<int:page>")
@admin_login_req
def commentlist(page):
    if page is None:
        page=1
    page_data = Comment.query.join(
        Video
    ).join(
        User
    ).filter(
        Comment.video_id==Video.id,
        Comment.user_id==User.id
    ).order_by(
        Comment.id.asc()
    ).paginate(page=page, per_page=10)
    return render_template('admin/comment_list.html',page_data=page_data)

@admin.route("/comment/delete/<int:id>")
@admin_login_req
def commentdelete(id):
    comment=Comment.query.get(id)
    db.session.delete(comment)
    db.session.commit()
    flash('评论删除成功','ok')
    return redirect(url_for('admin.commentlist',page=1))


@admin.route("/auth/list/")
@admin_login_req
def authlist():
    return render_template('admin/auth_list.html')


@admin.route("/auth/add/")
@admin_login_req
def authadd():
    return render_template('admin/auth_add.html')


@admin.route("/log/oplog/")
@admin_login_req
def oploglist():
    return render_template('admin/oplog_list.html')


@admin.route("/log/userlog/")
@admin_login_req
def userloglist():
    return render_template('admin/userloginlog_list.html')


@admin.route("/log/adminlog/")
@admin_login_req
def adminloglist():
    return render_template('admin/userloginlog_list.html')


@admin.route("/role/add/")
@admin_login_req
def roleadd():
    return render_template('admin/role_add.html')


@admin.route("/log/list/")
@admin_login_req
def rolelist():
    return render_template('admin/role_list.html')


@admin.route("/admin/add/")
@admin_login_req
def adminadd():
    return render_template('admin/admin_add.html')


@admin.route("/admin/list/")
@admin_login_req
def adminlist():
    return render_template('admin/admin_list.html')
