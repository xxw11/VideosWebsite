# coding:utf8
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField, SelectField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Length, Email, Regexp




class RegistForm(FlaskForm):
    name = StringField(
        label="账号",
        validators=[
            DataRequired("请输入账号")
        ],
        description='账号',
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入账号,可用中文，登录使用",
            "required": "required"
        },

    )
    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("请输入邮箱"),
            Email("邮箱格式不正确"),
        ],
        description='邮箱',
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入邮箱",
            "required": "required"

        }
    )
    phone = StringField(
        label="手机",
        validators=[
            DataRequired("请输入手机"),
            Regexp("^1(3|4|5|7|8)\d{9}$", message="手机格式是对的嘛？")
        ],
        description='手机',
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入手机号码",
            "required": "required"
        }
    )
    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("请输入密码")
        ],
        description='密码',
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入密码",
            "required": "required",
            "id":"password_input"
        }
    )
    usericon = FileField(
        label="头像",
        render_kw={
            "class": "btn-lg",
            "placeholder": "请输入密码",
        }
    )
    repwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("请确认密码"),
            EqualTo('pwd', message='两次密码不一致')
        ],
        description='密码',
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入密码",
            "required": "required",
            "id": "password_input",
        }
    )
    submit = SubmitField(
        '注册',
        render_kw={
            "class": "btn btn-lg btn-success btn-block",
        }
    )

    def validate_name(self, field):
        name = field.data
        from App import User
        user = User.query.filter_by(name=name).count
        if user == 1:
            raise ValidationError("昵称已经存在")

    def validate_email(self, field):
        email = field.data
        from App import User
        user = User.query.filter_by(email=email).count
        if user == 1:
            raise ValidationError("邮箱已经存在")

    def validate_phone(self, field):
        phone = field.data
        from App import User
        user = User.query.filter_by(phone=phone).count
        if user == 1:
            raise ValidationError("手机号码已经存在")

class LoginForm(FlaskForm):
    name = StringField(
        label="账号",
        validators=[
            DataRequired("请输入账号")
        ],
        description='账号',
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入账号",
            "required": "required"
        },

    )
    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("请输入密码")
        ],
        description='密码',
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入密码",
            "required": "required",
            "id": "password_input"
        }
    )
    submit = SubmitField(
        '登录',
        render_kw={
            "class": "btn btn-lg btn-success btn-block",
        }
    )

class UserdetailForm(FlaskForm):
    name = StringField(
        label="账号",
        validators=[
            # DataRequired("请输入账号")
        ],
        description='账号',
        render_kw={

            "class": "form-control",
            "placeholder": "请输入账号,可用中文，登录使用",

        },

    )
    email = StringField(
        label="邮箱",
        validators=[
            # DataRequired("请输入邮箱"),
            Email("邮箱格式不正确"),
        ],
        description='邮箱',
        render_kw={
            "class": "form-control",
            "placeholder": "请输入邮箱",


        }
    )
    phone = StringField(
        label="手机",
        validators=[
            # DataRequired("请输入手机"),
            Regexp("^1(3|4|5|7|8)\d{9}$", message="手机格式是对的嘛？")
        ],
        description='手机',
        render_kw={
            "class": "form-control",
            "placeholder": "请输入手机号码",
        }
    )
    face = FileField(
        label='头像',
        validators=[
            # DataRequired("请上传头像")
        ],
        description="头像",
    )
    info = TextAreaField(
        label="简介",
        validators=[
            # DataRequired("请输入视频的名称")
        ],
        description='简介',
        render_kw={
            'class': "form-control",
            'row': 10,
        },
    )
    submit = SubmitField(
        '确认',
        render_kw={
            "class": "btn btn-lg btn-info btn-block",
        }
    )

class PwdForm(FlaskForm):
    old_pwd = PasswordField(
        label='旧密码',
        validators=[
            DataRequired("请输入旧密码")
        ],
        description='旧密码',
        render_kw={
            'class': 'form-control',
            'placeholder':'请输入旧密码',
            "id": "password_input",
        }
    )
    new_pwd = PasswordField(
        label='新密码',
        validators=[
            DataRequired('请输入新密码')
        ],
        render_kw = {
            'class': 'form-control',
            'placeholder': '请输入旧密码',
            "id": "password_input",
        },
    )
    submit = SubmitField(
        '确认',
        render_kw={
            "class": "btn btn-lg btn-info btn-block",
        },
    )
    def validate_old_pwd(self,field):
        from flask import session
        pwd =field.data
        name=session['user']
        from App import User
        user = User.query.filter_by(
            name=name
        ).first()
        if not user.check_pwd(pwd):
            raise ValidationError('旧密码错误')

class VideoForm(FlaskForm):
    name = StringField(
        label="片名",
        validators=[
            DataRequired("请输入视频的名称")
        ],
        description='视频的名称',
        render_kw={
            'class': "form-control",
            'id': "input_name",
            'placeholder': "请输入视频的名称",
        },
    )
    url = FileField(
        label='视频文件',
        validators=[
            DataRequired("请上传视频文件！")
        ],
        description="文件",
    )
    info = TextAreaField(
        label="简介",
        validators=[
            DataRequired("请输入视频的名称")
        ],
        description='简介',
        render_kw={
            'class': "form-control",
            'row': 10,
        },
    )
    logo = FileField(
        label='封面',
        validators=[
            DataRequired("请上传封面")
        ],
        description="封面",
    )
    tag_id = SelectField(
        label='标签',
        validators=[
            DataRequired("请选择标签")
        ],
        coerce=int,
        # choices=[(v.id, v.name) for v in Tag()],
        description="标签",

    )
    length = StringField(
        label="视频时长",
        render_kw={
            'class': "form-control",
            'placeholder': "可输入输入视频时长",
        },
    )
    release_time = StringField(
        label="视频时间",
        description='视频时间',
        render_kw={
            'class': 'form-control',
            'placeholder': "可选择视频的年份月份等",
            'id': 'input_release_time'

        }
    )
    submit = SubmitField(
        '确认',
        render_kw={
            "class": "btn btn-primary",
        }
    )
