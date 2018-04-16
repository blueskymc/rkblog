#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
定义 view 模块
"""

___author__ = 'MaCong'

from flask import render_template, url_for, redirect, request, flash
from flask_login import login_required, current_user
from datetime import datetime
import time
import hashlib
import os
from . import manage
from .. import db, uploadset
from ..models import User, Blog, Comment, Label, Subject, Archive
from ..decorators import admin_required, rkuser_required
from .forms import ChangePasswordForm, BlogForm, SubjectForm
import logging

logging.basicConfig(level=logging.INFO)


# 修改密码
@manage.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('密码修改成功')
            return redirect(url_for('main.index'))
        else:
            flash('密码错误')
    return render_template('manage/change_password.html', form=form)


# 文章管理
@manage.route('/blogs')
@login_required
@rkuser_required
def manage_blogs():
    page = request.args.get('page', 1, type=int)
    if current_user.is_administrator():
        pagination = Blog.query.order_by(Blog.create_at.desc()).paginate(
            page, per_page=10, error_out=False)
    else:
        pagination = Blog.query.filter_by(author_id=current_user.id).order_by(Blog.create_at.desc()).paginate(
            page, per_page=10, error_out=False)

    blogs = pagination.items
    return render_template('manage/manage_blogs.html', blogs=blogs,
                           pagination=pagination, page=page)


# 写文章
@manage.route('/create-blog', methods=['GET', 'POST'])
@rkuser_required
@login_required
def create_blog():
    form = BlogForm()
    labs = Label.query.all()
    form.labels.choices = []
    form.labels.choices += [(r.name, r.name) for r in labs]
    subs = Subject.query.all()
    form.subjects.choices = [('无', '无')]
    form.subjects.choices += [(r.name, r.name) for r in subs]
    if form.validate_on_submit():
        blog = Blog(name=form.name.data,
                    summary=form.summary.data,
                    content=form.content.data,
                    author=current_user._get_current_object())

        # 上传附件
        if form.file.data:
            real_name = form.file.data.filename
            name = hashlib.md5((current_user.username + str(time.time())).encode('UTF-8')).hexdigest()[:15]
            uploadFile = uploadset.save(form.file.data, name=name+'.')
            blog.upload_file = uploadFile
            blog.upload_real_name = real_name

        # 博客添加专题
        subject = form.subjects.data
        if subject != '无':
            sub = Subject.query.filter_by(name=subject).first()
            blog.subject_id = sub.id
        db.session.add(blog)

        # 标签
        label = form.labels.data
        if label:
            lab = Label.query.filter_by(name=label).first()
            if lab:
                lab.blogs.append(blog)
                db.session.add(lab)

        # 专题添加博客
        if subject != '无':
            sub = Subject.query.filter_by(name=subject).first()
            if sub:
                sub.blogs.append(blog)
                db.session.add(sub)

        # 档案-时间分类
        str_time = datetime.now().strftime('%y-%m')
        arc = Archive.query.filter_by(name=str_time).first()
        # 若不存在，则新建标签
        if arc is None:
            newarc = Archive(name=str_time)
            newarc.blogs.append(blog)
            db.session.add(newarc)
        else:
            arc.blogs.append(blog)
            db.session.add(arc)

        db.session.commit()
        return redirect(url_for('main.blog', id=blog.id))
    return render_template('manage/create_blog.html', form=form)


# 编辑文章
@manage.route('/edit-blog/<int:id>', methods=['GET', 'POST'])
@rkuser_required
@login_required
def edit_blog(id):
    blog = Blog.query.get_or_404(id)
    form = BlogForm()
    labs = Label.query.all()
    form.labels.choices = []
    form.labels.choices += [(r.name, r.name) for r in labs]
    subs = Subject.query.all()
    form.subjects.choices = [('无', '无')]
    form.subjects.choices += [(r.name, r.name) for r in subs]
    if form.validate_on_submit():
        blog.name = form.name.data
        blog.summary = form.summary.data
        blog.content = form.content.data
        # 暴力修改，先删掉所有标签，再把标签栏里全部新增
        for l in blog.labels.all():
            l.blogs.remove(blog)
            db.session.add(l)
        db.session.commit()

        # 标签
        label = form.labels.data
        if label:
            lab = Label.query.filter_by(name=label).first()
            if lab:
                lab.blogs.append(blog)
                db.session.add(lab)

        # 上传附件
        if form.file.data:
            filePath = os.path.join('app\\_uploads', blog.upload_file)  # 先删除旧文件
            if os.path.isfile(filePath):
                os.remove(filePath)
            real_name = form.file.data.filename
            name = hashlib.md5((current_user.username + str(time.time())).encode('UTF-8')).hexdigest()[:15]
            uploadFile = uploadset.save(form.file.data, name=name + '.')
            blog.upload_file = uploadFile
            blog.upload_real_name = real_name

        # 专题
        subject = form.subjects.data
        if subject != '无':
            if subject != Subject.query.filter_by(id=blog.subject_id).first().name:  # 专题发生变化
                blog.subject_id = Subject.query.filter_by(name=subject).first().id  # 博客修改专题
                # 删除原专题中的博客
                for sub in Subject.query.all():
                    if blog in sub.blogs:
                        sub.blogs.remove(blog)
                        db.session.commit()
                # 专题添加博客
                sub = Subject.query.filter_by(name=subject).first()
                if sub:
                    sub.blogs.append(blog)
                    db.session.add(sub)
        db.session.commit()
        return redirect(url_for('main.blog', id=blog.id))
    form.name.data = blog.name
    form.summary.data = blog.summary
    form.content.data = blog.content
    sub_blog = Subject.query.filter_by(id=blog.subject_id).first()
    if sub_blog:
        form.subjects.data = sub_blog.name
    else:
        form.subjects.data = '无'
    lab_blog = blog.labels.first()
    if lab_blog:
        form.labels.data = lab_blog.name
    else:
        form.labels.data = 'DCS'
    return render_template('manage/edit_blog.html', form=form)


# 删除文章
@manage.route('/delete-blog/<int:id>')
@admin_required
@login_required
def delete_blog(id):
    blog = Blog.query.get_or_404(id)
    if blog.comments.all():
        for c in blog.comments.all():
            db.session.delete(c)
    # 将标签中的此文章删除
    if blog.labels.all():
        for lab in blog.labels.all():
            lab.blogs.remove(blog)
            db.session.add(lab)
    # 删除原专题中的博客
    for sub in Subject.query.all():
        if blog in sub.blogs:
            sub.blogs.remove(blog)
            db.session.commit()
    # 删除档案中的博客
    for arc in Archive.query.all():
        if blog in arc.blogs:
            arc.blogs.remove(blog)
            db.session.commit()
    db.session.delete(blog)
    db.session.commit()
    flash('文章已删除')
    return redirect(url_for('manage.manage_blogs',
                            page=request.args.get('page', 1, type=int)))


# 我的收藏
@manage.route('/collections')
@login_required
def manage_collections():
    page = request.args.get('page', 1, type=int)
    pagination = current_user.collections.paginate(
        page, per_page=10, error_out=False)
    blogs = pagination.items
    return render_template('manage/manage_collections.html', blogs=blogs,
                           pagination=pagination, page=page)


# 收藏
@manage.route('/collections/enable/<int:id>')
@login_required
def enable_collect(id):
    blog = Blog.query.get_or_404(id)
    user = current_user._get_current_object()
    if not blog.is_collected(user):
        user.collections.append(blog)
        db.session.add(user)
        db.session.commit()
        flash('收藏成功')
    else:
        flash('请勿重复收藏')
    # 在文章详情页操作
    if request.args.get('info', None) == 'blog':
        return redirect(url_for('main.blog', id=id))
    if request.args.get('info', None) == 'manage':
        return redirect(url_for('manage.manage_collections',
                                page=request.args.get('page', 1, type=int)))

    # 取消收藏


@manage.route('/collections/disable/<int:id>')
@login_required
def disable_collect(id):
    blog = Blog.query.get_or_404(id)
    user = current_user._get_current_object()
    if blog.is_collected(user):
        user.collections.remove(blog)
        db.session.add(user)
        db.session.commit()
        flash('取消收藏')
    else:
        flash('并未收藏该文章')
    # 在文章详情页操作
    if request.args.get('info', None) == 'blog':
        return redirect(url_for('main.blog', id=id))
    if request.args.get('info', None) == 'manage':
        return redirect(url_for('manage.manage_collections',
                                page=request.args.get('page', 1, type=int)))

    # 评论管理


@manage.route('/comments')
@admin_required
@login_required
def manage_comments():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.create_at.desc()).paginate(
        page, per_page=10, error_out=False)
    comments = pagination.items
    return render_template('manage/manage_comments.html', comments=comments,
                           pagination=pagination, page=page)


# 恢复评论
@manage.route('/comment/enable/<int:id>')
@admin_required
@login_required
def enable_comment(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    flash('已恢复该评论')
    if request.args.get('info', '') == 'blog':
        return redirect(url_for('main.blog', id=comment.blog.id,
                                page=request.args.get('page', 1, type=int)))
    return redirect(url_for('manage.manage_comments',
                            page=request.args.get('page', 1, type=int)))


# 屏蔽评论
@manage.route('/comment/disable/<int:id>')
@admin_required
@login_required
def disable_comment(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    flash('已屏蔽该评论')
    if request.args.get('info', '') == 'blog':
        return redirect(url_for('main.blog', id=comment.blog.id,
                                page=request.args.get('page', 1, type=int)))
    return redirect(url_for('manage.manage_comments',
                            page=request.args.get('page', 1, type=int)))


# 用户管理
@manage.route('/users')
@admin_required
@login_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.create_at.desc()).paginate(
        page, per_page=10, error_out=False)
    users = pagination.items
    return render_template('manage/manage_users.html', users=users,
                           pagination=pagination, page=page)


# 封禁用户
@manage.route('/user/disable/<int:id>')
@admin_required
@login_required
def disable_user(id):
    user = User.query.get_or_404(id)
    user.disabled = True
    db.session.add(user)
    db.session.commit()
    flash('用户已封禁')
    return redirect(url_for('manage.manage_users',
                            page=request.args.get('page', 1, type=int)))


# 解禁用户
@manage.route('/user/enable/<int:id>')
@admin_required
@login_required
def enable_user(id):
    user = User.query.get_or_404(id)
    user.disabled = False
    db.session.add(user)
    db.session.commit()
    flash('用户已解禁')
    return redirect(url_for('manage.manage_users',
                            page=request.args.get('page', 1, type=int)))

# 创建专题
@manage.route('/create-subject', methods=['GET', 'POST'])
@rkuser_required
@login_required
def create_subject():
    form = SubjectForm()
    subs = Subject.query.all()
    if form.validate_on_submit():
        name = form.name.data
        if name:
            sub = Subject.query.filter_by(name=name).first()
            # 若不存在，则新建标签
            if sub is None:
                newsub = Subject(name=name)
                db.session.add(newsub)
                flash('添加成功')
            else:
                flash('已存在该专题')

        db.session.commit()
    return render_template('manage/create_subject.html', form=form)

