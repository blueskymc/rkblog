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
from . import rk_manage
from .. import db
from ..models import User, Project, Dcs_Company, DCS, Rk_User
from ..decorators import admin_required, rkuser_required
from .forms import ProjectForm, DcsForm, DcsProForm
import logging

logging.basicConfig(level=logging.INFO)

# 热控管理主页
@rk_manage.route('/index')
@admin_required
@login_required
def manage():
    return render_template('rk_manage/manage.html')

# 创建工程
@rk_manage.route('/newproject', methods=['GET', 'POST'])
@admin_required
@login_required
def create_project():
    form = ProjectForm()
    uses = User.query.all()
    form.rk_user_owner.choices = [('无', '无')]
    form.rk_user_owner.choices += [(r.username, r.username) for r in uses]
    if form.validate_on_submit():
        rkuserowner = form.rk_user_owner.data

        if rkuserowner != '无':
            user = User.query.filter_by(username=rkuserowner).first()
            pro = Project(name=form.name.data,
                        customer=form.customer.data,
                        fullname=form.fullname.data,
                        rk_user=form.rk_user.data,
                        team_leader=form.team_leader.data,
                        project_leader=form.project_leader.data,
                        sign_date=form.sign_date.data,
                        execute_date=form.execute_date.data,
                        note=form.note.data,
                        author_id=user.id)
            db.session.add(pro)
        else:
            pro = Project(name=form.name.data,
                        customer=form.customer.data,
                        fullname=form.fullname.data,
                        rk_user=form.rk_user.data,
                        team_leader=form.team_leader.data,
                        project_leader=form.project_leader.data,
                        sign_date=form.sign_date.data,
                        execute_date=form.execute_date.data,
                        note=form.note.data)
            db.session.add(pro)
        return redirect(url_for('main.index'))
    return render_template('rk_manage/create_project.html', form=form)

# 创建DCS
@rk_manage.route('/newdcs', methods=['GET', 'POST'])
@admin_required
@login_required
def create_dcs():
    form = DcsForm()
    uses = User.query.all()
    form.type_dcs.choices = [('DCS', 'DCS'), ('PLC', 'PLC')]
    form.rk_user_owner.choices = [('无', '无')]
    form.rk_user_owner.choices += [(r.username, r.username) for r in uses]
    if form.validate_on_submit():
        rkuserowner = form.rk_user_owner.data

        if rkuserowner != '无':
            user = User.query.filter_by(username=rkuserowner).first()
            dcs = DCS(name=form.name.data,
                          company_name=form.company_name.data,
                          version=form.version.data,
                          plateform=form.plateform.data,
                          is_convert=form.is_convert.data,
                          type_dcs=form.type_dcs.data,
                          converter_developer=form.converter_developer.data,
                          alg_developer=form.alg_developer.data,
                          sourcecode_keeper=form.sourcecode_keeper.data,
                          sourcecode_owner=form.sourcecode_owner.data,
                          alg_keeper=form.alg_keeper.data,
                          alg_header=form.alg_header.data,
                          note=form.note.data,
                          author_id=user.id)
            db.session.add(dcs)
        else:
            dcs = DCS(name=form.name.data,
                          company_name=form.company_name.data,
                          version=form.version.data,
                          plateform=form.plateform.data,
                          is_convert=form.is_convert.data,
                          type_dcs=form.type_dcs.data,
                          converter_developer=form.converter_developer.data,
                          alg_developer=form.alg_developer.data,
                          sourcecode_keeper=form.sourcecode_keeper.data,
                          sourcecode_owner=form.sourcecode_owner.data,
                          alg_keeper=form.alg_keeper.data,
                          alg_header=form.alg_header.data,
                          note=form.note.data)
            db.session.add(dcs)
        return redirect(url_for('main.index'))
    return render_template('rk_manage/create_dcs.html', form=form)


# 创建DCS
@rk_manage.route('/relation', methods=['GET', 'POST'])
@admin_required
@login_required
def create_relation():
    dcses = DCS.query.all()
    pros = Project.query.all()
    form = DcsProForm()
    form.dcs.choices = []
    form.dcs.choices += [(r.name, r.name) for r in dcses]
    form.pro.choices = []
    form.pro.choices += [(r.name, r.name) for r in pros]
    if form.validate_on_submit():
        dcsSelect = DCS.query.filter_by(username=form.dcs.data).first()
        proSelect = Project.query.filter_by(username=form.pro.data).first()

        return redirect(url_for('main.index'))
    return render_template('rk_manage/dcs_project.html', form=form)