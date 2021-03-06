#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
定义 form 模块
"""

___author__ = 'MaCong'

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed
from .. import uploadset, uploadset_csv, uploadset_mdb

# 创建/编辑项目
class ProjectForm(FlaskForm):
    name = StringField('项目名', validators=[DataRequired()])
    customer = StringField('客户名')
    fullname = StringField('合同全称')
    rk_user_owner = SelectField('选择热控专业负责人', validators=[DataRequired()])
    rk_user = StringField('热控专业负责人', description='未与用户名关联，可以随便填写')
    team_leader = StringField('团队负责人')
    project_leader = StringField('项目负责人')
    sign_date = StringField('合同签订日期')
    execute_date = StringField('合同执行日期')
    file_star = FileField(validators=[FileAllowed(uploadset, u'只能上传文档、图片和压缩包！')])
    file_converter = FileField(validators=[FileAllowed(uploadset, u'只能上传文档、图片和压缩包！')])
    note = TextAreaField('备注')
    submit = SubmitField('提交')

# 创建/编辑DCS
class DcsForm(FlaskForm):
    name = StringField('DCS名称', validators=[DataRequired()])
    company_name = StringField('DCS公司')
    version = StringField('版本')
    plateform = StringField('操作系统')
    is_convert = BooleanField('能转换')
    type_dcs = SelectField('选择类型', validators=[DataRequired()])
    rk_user_owner = SelectField('选择热控专业负责人', validators=[DataRequired()])
    converter_developer = StringField('转换软件开发人')
    alg_developer = StringField('算法开发人')
    sourcecode_keeper = StringField('源程序保管人')
    sourcecode_owner = StringField('源程序负责人')
    alg_keeper = StringField('算法保管人')
    alg_header = StringField('算法前缀')
    file_star = FileField('上传star', validators=[FileAllowed(uploadset, u'只能上传文档、图片和压缩包！')])
    file_converter = FileField('上传转换软件', validators=[FileAllowed(uploadset, u'只能上传文档、图片和压缩包！')])
    note = TextAreaField('备注')
    submit = SubmitField('提交')

# 创建/编辑DCS与项目映射关系
class DcsProForm(FlaskForm):
    dcs = SelectField('选择DCS系统', validators=[DataRequired()])
    pro = SelectField('选择项目', validators=[DataRequired()])
    sys = SelectField('选择系统名称', validators=[DataRequired()])
    hmi = SelectField('选择画面方式', validators=[DataRequired()])
    cfg = SelectField('选择组态方式', validators=[DataRequired()])
    out = SelectField('选择出库项目', validators=[DataRequired()])
    submit = SubmitField('提交')

# 筛选项目
class ProjectFilterForm(FlaskForm):
    pro = SelectField('选择项目', validators=[DataRequired()])
    submit = SubmitField('筛选')

# 筛选DCS
class DcsFilterForm(FlaskForm):
    dcs = SelectField('选择DCS系统', validators=[DataRequired()])
    submit = SubmitField('筛选')

# 筛选关系
class RelFilterForm(FlaskForm):
    dcs = SelectField('选择DCS系统', validators=[DataRequired()])
    pro = SelectField('选择项目', validators=[DataRequired()])
    submit = SubmitField('筛选')

# 初始化，导入数据库
class InitForm(FlaskForm):
    file_mdb = FileField('上传mdb', validators=[FileAllowed(uploadset, u'只能上传mdb数据库！')])
    file_excel = FileField('上传excel', validators=[FileAllowed(uploadset, u'只能上传csv文件！')])
    submit = SubmitField('提交')