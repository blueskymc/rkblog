#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
定义 view 模块
"""

___author__ = 'MaCong'

import os
from flask_login import login_required, current_user
from flask import url_for, render_template, current_app, redirect, request, flash
from flask import send_from_directory, abort
from . import main
from .. import db
from ..decorators import rkuser_required
from ..models import User, Blog, Comment, Label, Subject, Archive, Subsystem, HmiMode, ConfigMode
from .forms import CreateCommentForm
import logging

logging.basicConfig(level=logging.INFO)

@main.route('/')
#@rkuser_required
def index():
    users = User.query.all()
    if not users:
        User.create_administrator()
        Blog.create_about_blog()
        Label.generate_default()
        Subsystem.generate_default()
        HmiMode.generate_default()
        ConfigMode.generate_default()

    if not current_user.is_active:
        flash('您还未登录，请先登录')
        return render_template('index.html')
    if not current_user.is_rkuser():
        flash('请找管理员注册成热控用户！')
        return render_template('index.html')
    page = request.args.get('page', 1, type=int)
    labname = request.args.get('label', None)
    subname = request.args.get('subject', None)
    archname = request.args.get('archive', None)
    # 选择了分类时
    if labname is not None:
        label = Label.query.filter_by(name=labname).first()
        pagination = label.blogs.order_by(Blog.create_at.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        blogs = pagination.items
        labels = Label.query.all()
        subjects = Subject.query.all()
        logging.info([p for p in pagination.iter_pages()])
        return render_template('index.html', users=users, blogs=blogs, labels=labels, subjects=subjects,
                               label=label, pagination=pagination)
    # 选择了专题时
    if subname is not None:
        subject = Subject.query.filter_by(name=subname).first()
        pagination = subject.blogs.order_by(Blog.create_at.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        blogs = pagination.items
        labels = Label.query.all()
        subjects = Subject.query.all()
        archives = Archive.query.all()
        logging.info([p for p in pagination.iter_pages()])
        return render_template('index.html', users=users, blogs=blogs, labels=labels, subjects=subjects, archives=archives,
                               subject=subject, pagination=pagination)
    # 选择了档案时
    if archname is not None:
        archive = Archive.query.filter_by(name=archname).first()
        pagination = archive.blogs.order_by(Blog.create_at.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        blogs = pagination.items
        labels = Label.query.all()
        subjects = Subject.query.all()
        archives = Archive.query.all()
        logging.info([p for p in pagination.iter_pages()])
        return render_template('index.html', users=users, blogs=blogs, labels=labels, subjects=subjects, archives=archives,
                               archive=archive, pagination=pagination)
    # 未选择分类和专题时
    pagination = Blog.query.order_by(Blog.create_at.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    blogs = pagination.items
    labels = Label.query.all()
    subjects = Subject.query.all()
    archives = Archive.query.all()
    return render_template('index.html', users=users, blogs=blogs, labels=labels, subjects=subjects, archives=archives,
                           pagination=pagination)

@main.route('/blog/<int:id>')
@rkuser_required
def blog(id):
    blog = Blog.query.get_or_404(id)
    form = CreateCommentForm()
    if form.validate_on_submit():
        comment = Comment(
            content = form.content.data,
            blog = blog,
            author = current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('评论已提交')
        return redirect(url_for('main.blog', id=blog.id))
    page = request.args.get('page', 1, type=int)
    pagination = blog.comments.order_by(Comment.create_at.desc()).paginate(
        page, per_page=6, error_out=False)
    comments = pagination.items
    return render_template('blog.html', blog=blog, comments=comments,
                            pagination=pagination, form=form, page=page)


@main.route('/download/<int:id>', methods=['GET'])
@rkuser_required
def download(id):
    blog = Blog.query.filter_by(id=id).first()
    if request.method == "GET":
        if os.path.isfile(os.path.join('app\\_uploads', blog.upload_file)):
            return send_from_directory(directory='_uploads', filename=blog.upload_file, as_attachment=True)
        abort(404)