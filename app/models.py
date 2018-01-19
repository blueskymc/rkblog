#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
定义 model 模块
"""

___author__ = 'MaCong'

from . import db, login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, current_user, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from markdown import markdown
import bleach, hashlib


# 收藏功能：Blog和User多对多关系的中间表
collections = db.Table('collections',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('blog_id', db.Integer, db.ForeignKey('blogs.id'))
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index = True)
    username = db.Column(db.String(64), unique=True, index = True)
    password_hash = db.Column(db.String(128))
    admin = db.Column(db.Boolean, default=False)
    rkuser = db.Column(db.Boolean, default=False)
    avatar_hash = db.Column(db.String(64))
    disabled = db.Column(db.Boolean, default=False)
    create_at = db.Column(db.DateTime, default=datetime.utcnow)
    blogs = db.relationship('Blog', backref='author', lazy= 'dynamic')
    dcses = db.relationship('DCS', backref='author', lazy= 'dynamic')
    projects = db.relationship('Project', backref='author', lazy= 'dynamic')
    comments = db.relationship('Comment', backref='author', lazy= 'dynamic')
    collections = db.relationship('Blog', secondary=collections,
                                  backref=db.backref('users', lazy='dynamic'),
                                  lazy='dynamic')

    def __init__(self, **kw):
        super(User, self).__init__(**kw)
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_administrator(self):
        return self.admin

    def is_rkuser(self):
        return self.rkuser

    # 生成Gravatar头像
    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.mp5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    @staticmethod
    def create_administrator():
        u = User(email='mc1515@163.com',
                 username='马聪',
                 password='123456',
                 rkuser=True,
                 admin=True)
        db.session.add(u)
        db.session.commit()

class AnonymousUser(AnonymousUserMixin):
    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class Blog(db.Model):
    __tablename__ = 'blogs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    summary = db.Column(db.Text)
    summary_html = db.Column(db.Text)
    content = db.Column(db.Text)
    content_html = db.Column(db.Text)
    upload_file = db.Column(db.Text)
    upload_real_name = db.Column(db.Text)
    create_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    archive_id = db.Column(db.Integer, db.ForeignKey('archives.id'))
    comments = db.relationship('Comment', backref='blog', lazy='dynamic')

    def is_collected(self, user):
        return self.users.filter_by(id=user.id).first() is not None

    @staticmethod
    def create_about_blog():
        if Blog.query.filter_by(id=998).first() is None:
            u = User.query.filter_by(id=1).first()
            b = Blog(id=998, name='关于本站', summary='简介', content='本网站主要记录仿真机热控方面的一些技巧和心得',
                     author=u)
            db.session.add(b)
            db.session.commit()

    @staticmethod
    def on_changed_summary(target, value, oldvalue, initiator):
        target.summary_html = bleach.linkify(markdown(value, output_format = 'html'))

    @staticmethod
    def on_changed_content(target, value, oldvalue, initiator):
        target.content_html = bleach.linkify(markdown(value, output_format = 'html'))

db.event.listen(Blog.summary, 'set', Blog.on_changed_summary)
db.event.listen(Blog.content, 'set', Blog.on_changed_content)

# 分类功能：Blog和Label多对多关系的中间表
classifications = db.Table('classifications',
    db.Column('blog_id', db.Integer, db.ForeignKey('blogs.id')),
    db.Column('label_id', db.Integer, db.ForeignKey('labels.id'))
)

class Label(db.Model):
    __tablename__= 'labels'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    type = db.Column(db.String(64))
    # 多对多关系模型
    blogs = db.relationship('Blog',
                          secondary=classifications,
                          backref=db.backref('labels', lazy='dynamic'),
                          lazy='dynamic')

    def __init__(self, **kw):
        super(Label, self).__init__(**kw)
        db.session.add(self)
        db.session.commit()
        L = ['danger', 'warning', 'info', 'success', 'primary', 'default']
        if self.type == None:
            index = (self.id + 6) % 6
            self.type = L[index]
            db.session.add(self)
            db.session.commit()

    @staticmethod
    def generate_default():
        if not Label.query.count():
            L = ['DCS', 'PLC', 'C#', 'C++', 'Ovation', 'ABB', 'T3000', 'TXP', '新华', '和利时', '国电智深', '南京科远',
                 'FOXBORO', '施耐德', '欧姆龙']
            for labname in L:
                l = Label(name=labname)
                db.session.add(l)
                db.session.commit()

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    create_at = db.Column(db.DateTime, default=datetime.utcnow, index = True)
    disabled = db.Column(db.Boolean, default=False)
    blog_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('blogs.id'))

# 专题
class Subject(db.Model):
    __tablename__= 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    blogs = db.relationship('Blog', backref='subject', lazy='dynamic')

    def __init__(self, **kw):
        super(Subject, self).__init__(**kw)
        db.session.add(self)
        db.session.commit()

# 按时间分类
class Archive(db.Model):
    __tablename__= 'archives'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    blogs = db.relationship('Blog', backref='archive', lazy='dynamic')

    def __init__(self, **kw):
        super(Archive, self).__init__(**kw)
        db.session.add(self)
        db.session.commit()

# DCS公司
class Dcs_Company(db.Model):
    __tablename__ = 'dcs_company'

    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(64))
    simple_name = db.Column(db.String(64))
    eng_name = db.Column(db.String(64))
    name = db.Column(db.String(64))
    note = db.Column(db.String(64))
    net_address = db.Column(db.String(64))

    def __init__(self, **kw):
        super(Dcs_Company, self).__init__(**kw)
        db.session.add(self)
        db.session.commit()

# DCS
class DCS(db.Model):
    __tablename__ = 'dcs'

    id = db.Column(db.Integer, primary_key=True)
    used_flag = db.Column(db.Boolean, default=False)
    type_dcs = db.Column(db.String(64))
    company_name = db.Column(db.String(64))
    name = db.Column(db.String(64))
    version = db.Column(db.String(64))
    plateform = db.Column(db.String(64))
    is_convert = db.Column(db.Boolean, default=False)
    converter_developer = db.Column(db.String(64))
    alg_developer = db.Column(db.String(64))
    sourcecode_keeper = db.Column(db.String(64))  # 源代码保管人
    sourcecode_owner = db.Column(db.String(64))  # 源码负责人
    alg_keeper = db.Column(db.String(64))
    alg_header = db.Column(db.String(64))  # 算法名前缀
    note = db.Column(db.String(64))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, **kw):
        super(DCS, self).__init__(**kw)
        db.session.add(self)
        db.session.commit()

# 热控人员
class Rk_User(db.Model):
    __tablename__ = 'rk_user'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    index = db.Column(db.String(64))
    name = db.Column(db.String(64))
    sex = db.Column(db.String(64))
    graduate_time = db.Column(db.String(64))
    work_time = db.Column(db.String(64))
    leave_time = db.Column(db.String(64))
    state = db.Column(db.String(64))
    university = db.Column(db.String(64))
    profession = db.Column(db.String(64))  # 专业
    zzmm = db.Column(db.String(64))  # 政治面貌
    birthday = db.Column(db.String(64))  # 源码负责人
    jiguan = db.Column(db.String(64))  # 籍贯
    gw_2013 = db.Column(db.String(64))  # 2013年岗位
    gw_2014 = db.Column(db.String(64))
    gw_2015 = db.Column(db.String(64))
    gw_2016 = db.Column(db.String(64))
    gw_2017 = db.Column(db.String(64))
    gw_2018 = db.Column(db.String(64))
    gw_2019 = db.Column(db.String(64))
    gw_2020 = db.Column(db.String(64))
    gw_2021 = db.Column(db.String(64))
    gw_2022 = db.Column(db.String(64))
    gw_2023 = db.Column(db.String(64))
    gw_2024 = db.Column(db.String(64))
    gw_2025 = db.Column(db.String(64))
    gw_2026 = db.Column(db.String(64))
    gw_2027 = db.Column(db.String(64))
    gw_2028 = db.Column(db.String(64))
    gw_2029 = db.Column(db.String(64))
    gw_2030 = db.Column(db.String(64))

    def __init__(self, **kw):
        super(Rk_User, self).__init__(**kw)
        db.session.add(self)
        db.session.commit()

# 分类功能：Blog和Label多对多关系的中间表
project_dcs = db.Table('project_dcs',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
    db.Column('dcs_id', db.Integer, db.ForeignKey('dcs.id'))
)

# 项目
class Project(db.Model):
    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer)
    name = db.Column(db.String(64))
    customer = db.Column(db.String(64))
    fullname = db.Column(db.String(64))
    rk_user = db.Column(db.String(64))
    team_leader = db.Column(db.String(64))
    project_leader = db.Column(db.String(64))
    sign_date = db.Column(db.String(64))
    execute_date = db.Column(db.String(64))
    note = db.Column(db.String(64))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # 多对多关系模型
    dcses = db.relationship('DCS',
                            secondary=project_dcs,
                            backref=db.backref('projects', lazy='dynamic'),
                            lazy='dynamic')

    def __init__(self, **kw):
        super(Project, self).__init__(**kw)
        db.session.add(self)
        db.session.commit()