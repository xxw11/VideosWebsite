# coding:utf8
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField, SelectField
from wtforms.validators import DataRequired, ValidationError

from App.models import Admin


class LoginForm(FlaskForm):
    account = StringField(
        label="账号",
        validators=[
            DataRequired("请输入账号")
        ],
        description='账号',
        render_kw={
            "class": "form-control",
            "placeholder": "请输入账号",
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
            "class": "form-control",
            "placeholder": "请输入密码",
            "required": "required"
        }
    )
    submit = SubmitField(
        '登录',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat",
        }
    )

    def validate_account(self, field):
        account = field.data
        admin = Admin.query.filter_by(name=account).count()
        if admin == 0:
            raise ValidationError("账号不存在")


class TagForm(FlaskForm):
    name = StringField(
        label="名称",
        validators=[
            DataRequired("请输入标签")
        ],
        description='标签',
        render_kw={
            'class': "form-control",
            'id': "input_name",
            'placeholder': "请输入标签名称！",
        },
    )
    submit = SubmitField(
        '添加',
        render_kw={
            "class": "btn btn-primary",
        }
    )


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
        label='文件',
        validators=[
            DataRequired("请上传文件！")
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


class PwdForm(FlaskForm):
    old_pwd = PasswordField(
        label='旧密码',
        validators=[
            DataRequired("请输入旧密码")
        ],
        description='旧密码',
        render_kw={
            'class': 'form-control',
            'placeholder':'请输入旧密码'
        }
    )
    new_pwd = PasswordField(
        label='新密码',
        validators=[
            DataRequired('请输入新密码')
        ],
        render_kw = {
            'class': 'form-control',
            'placeholder': '请输入旧密码'
        },
    )
    submit = SubmitField(
        '确认',
        render_kw={
            "class": "btn btn-primary",
        },
    )
    def validate_old_pwd(self,field):
        from flask import session
        pwd =field.data
        name=session['admin']
        admin = Admin.query.filter_by(
            name=name
        ).first()
        if not admin.check_pwd(pwd):
            raise ValidationError('旧密码错误')

class CommentForm(FlaskForm):
    content= TextAreaField(
        label="评论内容",
        validators=[
            DataRequired("请输入评论内容")
        ],
        description="评论内容",
        render_kw={
            'id':'input_content'
        }
    )
    submit = SubmitField(
        '提交评论',
        render_kw={
            'class':'btn btn-success',
            'id':'btn-sub'
        }
    )