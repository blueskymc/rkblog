#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
定义 form 模块
"""

___author__ = 'MaCong'

from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired

# 创建评论
class CreateCommentForm(FlaskForm):
	content = TextAreaField('说点什么？', validators=[DataRequired()])
	submit = SubmitField('提交评论')

# 搜索文章
class SerchBlogForm(FlaskForm):
	content = TextAreaField('搜索内容', validators=[DataRequired()])
	submit = SubmitField('搜索')
