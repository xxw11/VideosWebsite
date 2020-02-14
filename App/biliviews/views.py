import datetime
import os
import uuid
from functools import wraps

from flask import render_template, redirect, url_for, flash, request, session, Response
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from . import bili
from App.ext import rd
from ..ext import db


# 登录装饰器，访问控制
def user_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user') is None:
            flash('刚才那个页面加了访问控制，访问需要先登录', 'err')
            return redirect(url_for('bili.login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


# 修改上传文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex + fileinfo[-1]
    return filename


@bili.route("/")
def index():
    from App import Tag
    tags = Tag.query.all()
    from App import Video
    videos = Video.query.all()
    return render_template("/bili/index.html", tags=tags, videos=videos)


@bili.route("/login/", methods=['GET', 'POST'])
def login():
    from App.biliviews.forms import LoginForm
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        from App import User
        user = User.query.filter_by(name=data['name']).first()
        if user is None:
            flash('密码或账号错误', 'err')
            return redirect(url_for('bili.login'))
        if not user.check_pwd(data['pwd']):
            flash('密码或账号错误', 'err')
            return redirect(url_for('bili.login'))
        from flask import session
        session['user'] = user.name
        session['user_id'] = user.id
        from App import Userlog
        from flask import request
        userlog = Userlog(
            user_id=user.id,
            ip=request.remote_addr
        )
        db.session.add(userlog)
        db.session.commit()
        return redirect(url_for('bili.mine'))

    return render_template("/bili/usr/login.html", form=form)


@bili.route("/regist/", methods=['GET', 'POST'])
def regist():
    from App.biliviews.forms import RegistForm
    form = RegistForm()
    if form.validate_on_submit():
        data = form.data
        from App import User
        email_count = User.query.filter_by(email=data['email']).count()
        if email_count == 1:
            flash("邮箱已经存在了", 'err')
            return redirect(url_for('bili.regist'))
        phone_count = User.query.filter_by(phone=data['phone']).count()
        if phone_count == 1:
            flash("手机号已经存在了", 'err')
            return redirect(url_for('bili.regist'))
        user = User(
            name=data['name'],
            phone=data['phone'],
            email=data['email'],
            password=generate_password_hash(data['pwd']),
            uuid=uuid.uuid4().hex,
        )
        db.session.add(user)
        db.session.commit()
        flash("注册成功", 'ok')
    return render_template("/bili/usr/register.html", form=form, )


@bili.route("/logout/")
@user_login_req
def logout():
    from flask import session
    session.pop("user", None)
    session.pop("user_id", None)
    flash('退出啦', 'ok')
    return redirect(url_for('bili.login'))


@bili.route("/mine/", methods=['GET', 'POST'])
@user_login_req
def mine():
    from App.biliviews.forms import UserdetailForm
    form = UserdetailForm()
    from App import User
    user = User.query.get(int(session['user_id']))
    if request.method == 'GET':
        form.name.data = user.name
        form.email.data = user.email
        form.info.data = user.mood
        form.phone.data = user.phone
    if form.validate_on_submit():
        data = form.data
        from manage import app
        file_icon = secure_filename(form.face.data.filename)
        if not os.path.exists(app.config["FC_DIR"]):
            os.makedirs(app.config['FC_DIR'])
            # os.chmod(app.config['FC_DIR'], 'rw')
        user.icon = change_filename(file_icon)
        name_count = User.query.filter_by(name=data['name']).count()
        if data['name'] != user.name and name_count == 1:
            flash("用户名已经存在了", 'err')
            return redirect(url_for('bili.mine'))
        email_count = User.query.filter_by(email=data['email']).count()
        if data['email'] != user.email and email_count == 1:
            flash("邮箱已经存在了", 'err')
            return redirect(url_for('bili.mine'))
        phone_count = User.query.filter_by(phone=data['phone']).count()
        if data['phone'] != user.phone and phone_count == 1:
            flash("手机号已经存在了", 'err')
            return redirect(url_for('bili.mine'))
        user.name = data['name']
        user.email = data['email']
        user.phone = data['phone']
        user.mood = data['info']
        form.face.data.save(app.config['FC_DIR'] + user.icon)
        db.session.add(user)
        db.session.commit()

        flash("修改成功", 'ok')
        return redirect(url_for('bili.mine'))

    return render_template('bili/usr/mine.html', form=form, user=user)


@bili.route("/changepassword/", methods=['GET', 'POST'])
@user_login_req
def change_password():
    from App.biliviews.forms import PwdForm
    form = PwdForm()

    if form.validate_on_submit():
        from App import User
        data = form.data
        user = User.query.filter_by(id=session['user_id']).first()
        user.password = generate_password_hash(data['new_pwd'])
        db.session.add(user)
        db.session.commit()
        flash('修改密码成功,赶紧试试新密码吧', 'ok')
        return redirect(url_for('bili.logout'))
    return render_template('bili/usr/change_password.html', form=form)


@bili.route('/videos/<int:page><int:tagid>')
def videos(page,tagid):
    from App import Tag
    tags = Tag.query.all()
    from App import Video
    if tagid==0:
        page_data = Video.query.filter(

        ).order_by(
            Video.addtime.desc()
        ).paginate(page=page, per_page=10)
        videos = Video.query.all()
    else:
        page_data = Video.query.filter(
            Video.tag_id == tagid
        ).order_by(
            Video.addtime.desc()
        ).paginate(page=page, per_page=10)
        videos = Video.query.join(
            Tag
        ).filter(
            Video.tag_id==tagid
        )
    return render_template('bili/videos.html', tags=tags, videos=videos, page_data=page_data,tagid=tagid)


@bili.route('/upload/', methods=['GET', 'POST'])
@user_login_req
def upload():
    from App.biliviews.forms import VideoForm
    form = VideoForm()
    from App import Tag
    form.tag_id.choices = [(v.id, v.name) for v in Tag.query.all()]

    if form.validate_on_submit():
        from App import User
        user = User.query.get(int(session['user_id']))
        data = form.data
        file_url = secure_filename(form.url.data.filename)
        file_logo = secure_filename(form.logo.data.filename)
        from manage import app
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config['UP_DIR'], )
            # os.chmod(app.config['UP_DIR'], 'rw')
        url = user.name + change_filename(file_url)
        logo = user.name + change_filename(file_logo)
        flash('文件处理中，正在保存文件', 'info')
        form.url.data.save(app.config['UP_DIR'] + url)
        form.logo.data.save(app.config['UP_DIR'] + logo)
        flash('保存封面和视频成功，正在添加视频', 'info')
        from App import Video
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
            user_id=user.id
        )
        db.session.add(video)
        db.session.commit()
        flash('添加视频成功', 'ok')
        return redirect(url_for('bili.upload'))
    return render_template('bili/upload.html', form=form)


@bili.route('/comments/<int:page>')
@user_login_req
def comments(page):
    if page == None:
        page = 1
    from App import Comment
    from App import User
    from App import Video
    id = session['user_id']
    page_data = Comment.query.join(
        User,
    ).filter(
        User.id == id,
        Comment.user_id == User.id,
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template('bili/usr/comments.html', page_data=page_data)


@bili.route('/commentdel/<int:id>')
@user_login_req
def commentdel(id):
    from App import Comment
    comment = Comment.query.filter_by(id=id).first_or_404()
    db.session.delete(comment)
    db.session.commit()
    flash('删除评论成功', 'ok')
    return redirect(url_for('bili.comments', page=1))


@bili.route('/loginlog/')
@user_login_req
def loginlog():
    return render_template('bili/usr/loginlog.html')


# 添加视频收藏
@bili.route('/videocol/add/', methods=['GET'])
@user_login_req
def addvideocol():
    uid = int(request.args.get("uid", ""))
    vid = int(request.args.get("vid", ""))

    from App import Videocol
    videocol = Videocol.query.filter_by(
        user_id=uid,
        video_id=vid
    ).count()
    if videocol == 1:
        data = dict(ok=0)

    elif videocol == 0:
        videocol = Videocol(
            user_id=uid,
            video_id=vid
        )
        from App import Video
        video=Video.query.get(vid)
        video.col_num=video.col_num+1
        db.session.add(videocol)
        db.session.add(video)
        db.session.commit()
        data = dict(ok=1)
    import json
    return json.dumps(data)

# 添加视频点赞
@bili.route('/videoup/add/', methods=['GET'])
@user_login_req
def addvideoup():
    uid = int(request.args.get("uid", ""))
    vid = int(request.args.get("vid", ""))

    from App import Videoup
    videoup = Videoup.query.filter_by(
        user_id=uid,
        video_id=vid
    ).count()
    if videoup == 1:
        data = dict(ok=0)

    elif videoup == 0:
        videoup = Videoup(
            user_id=uid,
            video_id=vid
        )
        from App import Video
        video=Video.query.get(vid)
        video.up_num=video.up_num+1
        db.session.add(videoup)
        db.session.add(video)
        db.session.commit()
        data = dict(ok=1)
    import json
    return json.dumps(data)


@bili.route('/videocol/')
@user_login_req
def videocol():
    from App import Video
    uid=session['user_id']
    from App import Videocol
    videos=Video.query.join(
        Videocol
    ).filter(
        Videocol.user_id==uid,
        Videocol.video_id==Video.id
    )
    return render_template('bili/usr/videocol.html',videos=videos)


@bili.route('/myvideos/')
@user_login_req
def myvideos():
    return render_template('bili/usr/myvideos.html')


# 搜索
@bili.route('/search/<int:page>')
def search(page=None):
    if page is None:
        page = 1
    key = request.args.get('search_info', '')
    from App import Video
    num = Video.query.filter(
        Video.title.ilike('%' + key + '%')).count()
    page_data = Video.query.filter(
        Video.title.ilike('%' + key + '%')
    ).order_by(
        Video.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template('bili/search.html', key=key, page_data=page_data, num=num)


@bili.route('/play/<int:id>/<int:page>', methods=['GET', 'POST'])
def play(id, page=None):
    if page == None:
        page = 1
    from App import Comment
    from App import Video
    from App import Tag
    from App import User
    video = Video.query.join(Tag).filter(
        Tag.id == Video.tag_id,
        Video.id == int(id),
        User.id == Video.user_id
    ).first_or_404()

    page_data = Comment.query.join(
        User
    ).filter(
        Comment.video_id == int(id),
        User.id == Comment.user_id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=5)

    comment_num = Comment.query.join(
        Video
    ).filter(
        Video.id == int(id),
        Video.id == Comment.video_id,
    ).count()
    video.playnum = video.playnum + 1
    from App.adminviews.forms import CommentForm
    form = CommentForm()

    if 'user' in session and form.validate_on_submit():
        data = form.data

        comment = Comment(
            content=data['content'],
            video_id=video.id,
            user_id=session['user_id'],
        )
        db.session.add(comment)
        db.session.commit()
        video.commentnum = video.commentnum + 1
        flash('评论成功', 'ok')
        db.session.add(video)
        db.session.commit()
        return redirect(url_for('bili.play', id=video.id, page=1))
    db.session.add(video)
    db.session.commit()
    return render_template('bili/play.html', video=video, form=form, page_data=page_data, comment_num=comment_num,
                           id=id)

@bili.route("/tm/", methods=["GET", "POST"])
def tm():
    import json

    if request.method == "GET":
        #获取弹幕消息队列
        id = request.args.get('id')
        key = "video" + str(id)

        if rd.llen(key):
            msgs = rd.lrange(key, 0, 2999)
            res = {
                "code": 1,
                "danmaku": [json.loads(v) for v in msgs]
            }
        else:
            res = {
                "code": 1,
                "danmaku": []
            }
        resp = json.dumps(res)
    if request.method == "POST":
        #添加弹幕
        data = json.loads(request.get_data())
        msg = {
            "__v": 0,
            "author": data["author"],
            "time": data["time"],
            "text": data["text"],
            "color": data["color"],
            "type": data['type'],
            "ip": request.remote_addr,
            "_id": datetime.datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex,
            "player": [
                data["player"]
            ]
        }
        res = {
            "code": 1,
            "data": msg
        }
        resp = json.dumps(res)
        rd.lpush("video" + str(data["player"]), json.dumps(msg))
    return Response(resp, mimetype='application/json')