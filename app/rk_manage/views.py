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
from ..models import User, Project, Dcs_Company, DCS, Rk_User, Subsystem, HmiMode, ConfigMode
from ..decorators import admin_required, rkuser_required
from ..MySqlHelper import MySQL_Utils
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
        return redirect(url_for('rk_manage.show_project'))
    return render_template('rk_manage/create_project.html', form=form)

# 编辑工程
@rk_manage.route('/edit_project/<int:id>', methods=['GET', 'POST'])
@admin_required
@login_required
def edit_project(id):
    pro = Project.query.get_or_404(id)
    form = ProjectForm()
    uses = User.query.all()
    form.rk_user_owner.choices = [('无', '无')]
    form.rk_user_owner.choices += [(r.username, r.username) for r in uses]
    if form.validate_on_submit():
        rkuserowner = form.rk_user_owner.data
        pro_edit = Project.query.filter_by(id=id).first()
        pro_edit.name = form.name.data
        pro_edit.customer = form.customer.data,
        pro_edit.fullname = form.fullname.data,
        pro_edit.rk_user = form.rk_user.data,
        pro_edit.team_leader = form.team_leader.data,
        pro_edit.project_leader = form.project_leader.data,
        pro_edit.sign_date = form.sign_date.data,
        pro_edit.execute_date = form.execute_date.data,
        pro_edit.note = form.note.data
        if rkuserowner != '无':
            user = User.query.filter_by(username=rkuserowner).first()
            pro_edit.author_id = user.id
        db.session.commit()
        return redirect(url_for('rk_manage.show_project'))
    form.name.data = pro.name
    form.customer.data = pro.customer
    form.fullname.data = pro.fullname
    form.rk_user.data = pro.rk_user
    form.team_leader.data = pro.team_leader
    form.project_leader.data = pro.project_leader
    form.sign_date.data = pro.sign_date
    form.execute_date.data = pro.execute_date
    form.note.data = pro.note
    form.execute_date.data = pro.execute_date
    if pro.author_id:
        form.rk_user_owner.data = User.query.filter_by(id=pro.author_id).first().username
    else:
        form.rk_user_owner.data = '无'
    return render_template('rk_manage/edit_project.html', form=form)

# 删除工程
@rk_manage.route('/delete-project/<int:id>')
@admin_required
@login_required
def delete_project(id):
    pro = Project.query.get_or_404(id)
    db.session.delete(pro)
    db.session.commit()
    flash('项目已删除')
    return redirect(url_for('rk_manage.show_project'))

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
        return redirect(url_for('rk_manage.show_dcs'))
    return render_template('rk_manage/create_dcs.html', form=form)

# 编辑DCS
@rk_manage.route('/edit_dcs/<int:id>', methods=['GET', 'POST'])
@admin_required
@login_required
def edit_dcs(id):
    dcs_old = Project.query.get_or_404(id)
    form = DcsForm()
    uses = User.query.all()
    form.type_dcs.choices = [('DCS', 'DCS'), ('PLC', 'PLC')]
    form.rk_user_owner.choices = [('无', '无')]
    form.rk_user_owner.choices += [(r.username, r.username) for r in uses]
    if form.validate_on_submit():
        rkuserowner = form.rk_user_owner.data
        dcs_edit = DCS.query.filter_by(id=id).first()
        dcs_edit.name = form.name.data
        dcs_edit.company_name = form.company_name.data
        dcs_edit.version = form.version.data
        dcs_edit.plateform = form.plateform.data
        dcs_edit.is_convert = form.is_convert.data
        dcs_edit.type_dcs = form.type_dcs.data
        dcs_edit.converter_developer = form.converter_developer.data
        dcs_edit.alg_developer = form.alg_developer.data
        dcs_edit.sourcecode_keeper = form.sourcecode_keeper.data
        dcs_edit.sourcecode_owner = form.sourcecode_owner.data
        dcs_edit.alg_keeper = form.alg_keeper.data
        dcs_edit.alg_header = form.alg_header.data
        dcs_edit.note = form.note.data
        if rkuserowner != '无':
            user = User.query.filter_by(username=rkuserowner).first()
            dcs_edit.author_id = user.id
        db.session.commit()
        return redirect(url_for('rk_manage.show_dcs'))

    form.name.data = dcs_old.name
    form.company_name.data = dcs_old.company_name
    form.version.data = dcs_old.version
    form.plateform.data = dcs_old.plateform
    form.is_convert.data = dcs_old.is_convert
    form.type_dcs.data = dcs_old.type_dcs
    form.converter_developer.data = dcs_old.converter_developer
    form.alg_developer.data = dcs_old.alg_developer
    form.sourcecode_keeper.data = dcs_old.sourcecode_keeper
    form.sourcecode_owner.data = dcs_old.sourcecode_owner
    form.alg_keeper.data = dcs_old.alg_keeper
    form.alg_header.data = dcs_old.alg_header
    form.note.data = dcs_old.note
    if dcs_old.author_id:
        form.rk_user_owner.data = User.query.filter_by(id=dcs_old.author_id).first().username
    else:
        form.rk_user_owner.data = '无'
    return render_template('rk_manage/edit_dcs.html', form=form)

# 创建DCS与工程关系
@rk_manage.route('/relation', methods=['GET', 'POST'])
@rkuser_required
@login_required
def create_relation():
    dcses = DCS.query.all()
    pros = Project.query.all()
    subs = Subsystem.query.all()
    hmis = HmiMode.query.all()
    cfgs = ConfigMode.query.all()
    form = DcsProForm()
    form.dcs.choices = []
    form.dcs.choices += [(r.name, r.name) for r in dcses]
    form.pro.choices = []
    form.pro.choices += [(r.name, r.name) for r in pros]
    form.sys.choices = []
    form.sys.choices += [(r.name, r.name) for r in subs]
    form.hmi.choices = []
    form.hmi.choices += [(r.name, r.name) for r in hmis]
    form.cfg.choices = []
    form.cfg.choices += [(r.name, r.name) for r in cfgs]
    if form.validate_on_submit():
        dcsSelect = DCS.query.filter_by(name=form.dcs.data).first()
        proSelect = Project.query.filter_by(name=form.pro.data).first()
        sysSelect = Subsystem.query.filter_by(name=form.sys.data).first()
        hmiSelect = HmiMode.query.filter_by(name=form.hmi.data).first()
        cfgSelect = ConfigMode.query.filter_by(name=form.cfg.data).first()
        if dcsSelect is not None and proSelect is not None:
            sql = MySQL_Utils()
            sqlStr = "INSERT INTO project_dcs VALUES (%d, %d, %d, %d, %d);" \
                     % (proSelect.id, dcsSelect.id, sysSelect.id, hmiSelect.id, cfgSelect.id)
            sql.exec_txsql(sqlStr)
        return redirect(url_for('rk_manage.show_relations'))
    return render_template('rk_manage/dcs_project.html', form=form)

# 编辑DCS与工程关系
@rk_manage.route('/edit_relation/dcsname/proname', methods=['GET', 'POST'])
@rkuser_required
@login_required
def edit_relation(dcsname, proname):
    if dcsname is None:
        pass
    if proname is None:
        pass
    sql = MySQL_Utils()
    dcses = DCS.query.all()
    pros = Project.query.all()
    subs = Subsystem.query.all()
    hmis = HmiMode.query.all()
    cfgs = ConfigMode.query.all()
    form = DcsProForm()
    form.dcs.choices = []
    form.dcs.choices += [(r.name, r.name) for r in dcses]
    form.pro.choices = []
    form.pro.choices += [(r.name, r.name) for r in pros]
    form.sys.choices = []
    form.sys.choices += [(r.name, r.name) for r in subs]
    form.hmi.choices = []
    form.hmi.choices += [(r.name, r.name) for r in hmis]
    form.cfg.choices = []
    form.cfg.choices += [(r.name, r.name) for r in cfgs]
    if form.validate_on_submit():
        dcsSelect = DCS.query.filter_by(name=form.dcs.data).first()
        proSelect = Project.query.filter_by(name=form.pro.data).first()
        sysSelect = Subsystem.query.filter_by(name=form.sys.data).first()
        hmiSelect = HmiMode.query.filter_by(name=form.hmi.data).first()
        cfgSelect = ConfigMode.query.filter_by(name=form.cfg.data).first()
        if dcsSelect is not None and proSelect is not None:
            sqlStr = "INSERT INTO project_dcs VALUES (%d, %d, %d, %d, %d);" \
                     % (proSelect.id, dcsSelect.id, sysSelect.id, hmiSelect.id, cfgSelect.id)
            sql.exec_txsql(sqlStr)
        return redirect(url_for('rk_manage.show_relations'))
    sql_select = "SELECT * FROM project_dcs WHERE id="
    return render_template('rk_manage/edit_dcs_project.html', form=form)

# 显示工程
@rk_manage.route('/showprojects', methods=['GET'])
@rkuser_required
@login_required
def show_project():
    pros = Project.query.all()
    return render_template('rk_manage/show_project.html', projects=pros)

# 显示DCS
@rk_manage.route('/showdcses', methods=['GET'])
@rkuser_required
@login_required
def show_dcs():
    if current_user.is_administrator():
        dcs = DCS.query.all()
        return render_template('rk_manage/show_dcs.html', dcses=dcs)
    else:
        flash('您不是管理员')
        #return redirect(url_for('rk_manage.manage'))


# 显示DCS和工程关系
@rk_manage.route('/showrelations', methods=['GET'])
@rkuser_required
@login_required
def show_relations():
    sql = MySQL_Utils()
    sqlstr = "SELECT vdp.dcsname, vdp.projectname, vdp.sysname, vdp.hminame, vdp.cfgname FROM view_dcs_project vdp"
    #sqlstr = "SELECT vdp.dcsname, vdp.projectname, vdp.sysname FROM view_dcs_project vdp WHERE vdp.dcsname="
    result = sql.exec_sql(sqlstr)
    relations = list(result)
    return render_template('rk_manage/show_relations.html', rels=relations)


# 显示工程和DCS关系
@rk_manage.route('/showrelations/pro2dcs', methods=['GET'])
@rkuser_required
@login_required
def show_relations_pd():
    sql = MySQL_Utils()
    sqlstr = "SELECT vpd.dcsname, vpd.projectname, vpd.sysname, vpd.hminame, vpd.cfgname FROM view_project_dcs vpd"
    #sqlstr = "SELECT vdp.dcsname, vdp.projectname, vdp.sysname FROM view_dcs_project vdp WHERE vdp.dcsname="
    result = sql.exec_sql(sqlstr)
    relations = list(result)
    return render_template('rk_manage/show_relations_pd.html', rels=relations)