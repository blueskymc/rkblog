#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
定义 form 模块
"""

___author__ = 'MaCong'

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, EqualTo
from flask_pagedown.fields import PageDownField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from .. import uploadset

# 修改密码
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='两次输入密码不一致')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('确认修改')

# 创建/编辑博客
class BlogForm(FlaskForm):
    name = StringField('标题', validators=[DataRequired()])
    subjects = SelectField('选择专题', validators=[DataRequired()])
    labels = SelectMultipleField("分类", choices=[])
    label = StringField('文章分类', validators=[DataRequired()])
    summary = TextAreaField('摘要', validators=[DataRequired()])
    content = PageDownField('内容', validators=[DataRequired()])
    file = FileField(validators=[FileAllowed(uploadset, u'只能上传文档、图片和压缩包！'),
                                 FileRequired(u'文件未选择！')])
    submit = SubmitField('发表文章')

# 创建/编辑专题
class SubjectForm(FlaskForm):
    name = StringField('专题名称', validators=[DataRequired()])
    submit = SubmitField('创建')