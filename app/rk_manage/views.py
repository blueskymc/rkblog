#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
定义 view 模块
"""

___author__ = 'MaCong'

from flask import render_template, url_for, redirect, request, flash
from flask_login import login_required, current_user
from flask import send_from_directory, abort
from datetime import datetime
import time
import hashlib
import os
from . import rk_manage
from .. import db, uploadset
from ..models import User, Project, Project_Dcs, DCS, Rk_User, Subsystem, HmiMode, ConfigMode
from ..decorators import admin_required, rkuser_required
from ..MySqlHelper import MySQL_Utils
from ..AccessHelper import AccessHelper
from .forms import *
import logging

logging.basicConfig(level=logging.INFO)

# 热控管理主页
@rk_manage.route('/index')
@rkuser_required
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
                        rk_user=rkuserowner,
                        team_leader=form.team_leader.data,
                        project_leader=form.project_leader.data,
                        sign_date=form.sign_date.data,
                        execute_date=form.execute_date.data,
                        note=form.note.data,
                        author_id=user.id)

            if form.file_star.data:
                pro.upload_star_real_name = form.file_star.data.filename
                name_star = hashlib.md5((current_user.username + str(time.time())).encode('UTF-8')).hexdigest()[:15]
                pro.upload_star_file = uploadset.save(form.file_star.data, name=name_star + '.')
                pro.upload_star_time = datetime.utcnow().date()

            if form.file_converter.data:
                pro.upload_converter_real_name = form.file_converter.data.filename
                name_converter = hashlib.md5((current_user.username + str(time.time())).encode('UTF-8')).hexdigest()[
                                 :15]
                pro.upload_converter_file = uploadset.save(form.file_converter.data, name=name_converter + '.')
                pro.upload_converter_time = datetime.utcnow().date()
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
            if form.file_star.data:
                pro.upload_star_real_name = form.file_star.data.filename
                name_star = hashlib.md5((current_user.username + str(time.time())).encode('UTF-8')).hexdigest()[:15]
                pro.upload_star_file = uploadset.save(form.file_star.data, name=name_star + '.')
                pro.upload_star_time = datetime.utcnow().date()
                pro.upload_star_user = current_user.username

            if form.file_converter.data:
                pro.upload_converter_real_name = form.file_converter.data.filename
                name_converter = hashlib.md5((current_user.username + str(time.time())).encode('UTF-8')).hexdigest()[
                                 :15]
                pro.upload_converter_file = uploadset.save(form.file_converter.data, name=name_converter + '.')
                pro.upload_converter_time = datetime.utcnow().date()
                pro.upload_converter_user = current_user.username
            db.session.add(pro)
        return redirect(url_for('rk_manage.show_project'))
    return render_template('rk_manage/create_project.html', form=form)

# 编辑工程
@rk_manage.route('/edit_project/<int:id>', methods=['GET', 'POST'])
@rkuser_required
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
        pro_edit.rk_user = rkuserowner,
        pro_edit.team_leader = form.team_leader.data,
        pro_edit.project_leader = form.project_leader.data,
        pro_edit.sign_date = form.sign_date.data,
        pro_edit.execute_date = form.execute_date.data,
        pro_edit.note = form.note.data
        if rkuserowner != '无':
            user = User.query.filter_by(username=rkuserowner).first()
            pro_edit.author_id = user.id
        db.session.commit()
        if form.file_star.data:
            filePath = os.path.join('app\\_uploads', pro_edit.upload_star_file)  # 先删除旧文件
            if os.path.isfile(filePath):
                os.remove(filePath)
            pro_edit.upload_star_real_name = form.file_star.data.filename
            name_star = hashlib.md5((current_user.username + str(time.time())).encode('UTF-8')).hexdigest()[:15]
            pro_edit.upload_star_file = uploadset.save(form.file_star.data, name=name_star + '.')
            pro_edit.upload_star_time = datetime.utcnow().date()
            pro_edit.upload_star_user = current_user.username

        if form.file_converter.data:
            filePath = os.path.join('app\\_uploads', pro_edit.upload_converter_file)  # 先删除旧文件
            if os.path.isfile(filePath):
                os.remove(filePath)
            pro_edit.upload_converter_real_name = form.file_converter.data.filename
            name_converter = hashlib.md5((current_user.username + str(time.time())).encode('UTF-8')).hexdigest()[:15]
            pro_edit.upload_converter_file = uploadset.save(form.file_converter.data, name=name_converter + '.')
            pro_edit.upload_converter_time = datetime.utcnow().date()
            pro_edit.upload_converter_user = current_user.username

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
                  alg_keeper=rkuserowner,
                  alg_header=form.alg_header.data,
                  note=form.note.data)
        if rkuserowner != '无':
            user = User.query.filter_by(username=rkuserowner).first()
            dcs.author_id = user.id

        if form.file_star.data:
            dcs.upload_star_real_name = form.file_star.data.filename
            name_star = hashlib.md5((current_user.username + str(time.time())).encode('UTF-8')).hexdigest()[:15]
            dcs.upload_star_file = uploadset.save(form.file_star.data, name=name_star+'.')
            dcs.upload_star_time = datetime.utcnow().date()
            dcs.upload_star_user = current_user.username

        if form.file_converter.data:
            dcs.upload_converter_real_name = form.file_converter.data.filename
            name_converter = hashlib.md5((current_user.username + str(time.time())).encode('UTF-8')).hexdigest()[:15]
            dcs.upload_converter_file = uploadset.save(form.file_converter.data, name=name_converter+'.')
            dcs.upload_converter_time = datetime.utcnow().date()
            dcs.upload_converter_user = current_user.username
        db.session.add(dcs)
        return redirect(url_for('rk_manage.show_dcs'))
    return render_template('rk_manage/create_dcs.html', form=form)

# 编辑DCS
@rk_manage.route('/edit_dcs/<int:id>', methods=['GET', 'POST'])
@rkuser_required
@login_required
def edit_dcs(id):
    dcs_old = DCS.query.get_or_404(id)
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
        dcs_edit.alg_keeper = rkuserowner
        dcs_edit.alg_header = form.alg_header.data
        dcs_edit.note = form.note.data
        if rkuserowner != '无':
            user = User.query.filter_by(username=rkuserowner).first()
            dcs_edit.author_id = user.id

        if form.file_star.data:
            filePath = os.path.join('app\\_uploads', dcs_edit.upload_star_file)  # 先删除旧文件
            if os.path.isfile(filePath):
                os.remove(filePath)
            dcs_edit.upload_star_real_name = form.file_star.data.filename
            name_star = hashlib.md5((current_user.username + str(time.time())).encode('UTF-8')).hexdigest()[:15]
            dcs_edit.upload_star_file = uploadset.save(form.file_star.data, name=name_star + '.')
            dcs_edit.upload_star_time = datetime.utcnow().date()
            dcs_edit.upload_star_user = current_user.username

        if form.file_converter.data:
            filePath = os.path.join('app\\_uploads', dcs_edit.upload_converter_file)  # 先删除旧文件
            if os.path.isfile(filePath):
                os.remove(filePath)
            dcs_edit.upload_converter_real_name = form.file_converter.data.filename
            name_converter = hashlib.md5((current_user.username + str(time.time())).encode('UTF-8')).hexdigest()[:15]
            dcs_edit.upload_converter_file = uploadset.save(form.file_converter.data, name=name_converter + '.')
            dcs_edit.upload_converter_time = datetime.utcnow().date()
            dcs_edit.upload_converter_user = current_user.username
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

# 创建DCS与工程关系-非ORM
# @rk_manage.route('/relation', methods=['GET', 'POST'])
# @rkuser_required
# @login_required
# def create_relation():
#     dcses = DCS.query.all()
#     pros = Project.query.all()
#     subs = Subsystem.query.all()
#     hmis = HmiMode.query.all()
#     cfgs = ConfigMode.query.all()
#     form = DcsProForm()
#     form.dcs.choices = []
#     form.dcs.choices += [(r.name, r.name) for r in dcses]
#     form.pro.choices = []
#     form.pro.choices += [(r.name, r.name) for r in pros]
#     form.sys.choices = []
#     form.sys.choices += [(r.name, r.name) for r in subs]
#     form.hmi.choices = []
#     form.hmi.choices += [(r.name, r.name) for r in hmis]
#     form.cfg.choices = []
#     form.cfg.choices += [(r.name, r.name) for r in cfgs]
#     if form.validate_on_submit():
#         dcsSelect = DCS.query.filter_by(name=form.dcs.data).first()
#         proSelect = Project.query.filter_by(name=form.pro.data).first()
#         sysSelect = Subsystem.query.filter_by(name=form.sys.data).first()
#         hmiSelect = HmiMode.query.filter_by(name=form.hmi.data).first()
#         cfgSelect = ConfigMode.query.filter_by(name=form.cfg.data).first()
#         if dcsSelect is not None and proSelect is not None:
#             sql = MySQL_Utils()
#             sqlStr = "INSERT INTO project_dcs VALUES (%d, %d, %d, %d, %d);" \
#                      % (proSelect.id, dcsSelect.id, sysSelect.id, hmiSelect.id, cfgSelect.id)
#             sql.exec_txsql(sqlStr)
#         return redirect(url_for('rk_manage.show_relations'))
#     return render_template('rk_manage/dcs_project.html', form=form)

# 创建DCS与工程关系-ORM
@rk_manage.route('/relation', methods=['GET', 'POST'])
@rkuser_required
@login_required
def create_relation():
    dcses = DCS.query.all()
    pros = get_cur_user_pros()
    pros_out = Project.query.all()
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
    form.out.choices = [('无', '无')]
    form.out.choices += [(r.name, r.name) for r in pros_out]
    if form.validate_on_submit():
        dcsSelect = DCS.query.filter_by(name=form.dcs.data).first()
        proSelect = Project.query.filter_by(name=form.pro.data).first()
        sysSelect = Subsystem.query.filter_by(name=form.sys.data).first()
        hmiSelect = HmiMode.query.filter_by(name=form.hmi.data).first()
        cfgSelect = ConfigMode.query.filter_by(name=form.cfg.data).first()
        if dcsSelect is not None and proSelect is not None:
            pro_dcs = Project_Dcs(project_id=proSelect.id,
                                  dcs_id=dcsSelect.id,
                                  sys_id=sysSelect.id,
                                  hmi_id=hmiSelect.id,
                                  cfg_id=cfgSelect.id,
                                  pro_out=form.out.data)
            db.session.add(pro_dcs)
        return redirect(url_for('rk_manage.show_relations'))
    return render_template('rk_manage/dcs_project.html', form=form)

# 编辑DCS与工程关系
@rk_manage.route('/edit_relation/<int:id>', methods=['GET', 'POST'])
@rkuser_required
@login_required
def edit_relation(id):
    pd_edit = Project_Dcs.query.filter_by(id=id).first()

    dcses = DCS.query.all()
    pros = get_cur_user_pros()
    pros_out = Project.query.all()
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
    form.out.choices = [('无', '无')]
    form.out.choices += [(r.name, r.name) for r in pros_out]
    if form.validate_on_submit():
        dcsSelect = DCS.query.filter_by(name=form.dcs.data).first()
        proSelect = Project.query.filter_by(name=form.pro.data).first()
        sysSelect = Subsystem.query.filter_by(name=form.sys.data).first()
        hmiSelect = HmiMode.query.filter_by(name=form.hmi.data).first()
        cfgSelect = ConfigMode.query.filter_by(name=form.cfg.data).first()
        if dcsSelect is not None and proSelect is not None:
            pd_edit.project_id = proSelect.id
            pd_edit.dcs_id = dcsSelect.id
            pd_edit.sys_id = sysSelect.id
            pd_edit.hmi_id = hmiSelect.id
            pd_edit.cfg_id = cfgSelect.id
            pd_edit.pro_out = form.out.data
            db.session.add(pd_edit)
        return redirect(url_for('rk_manage.show_relations'))
    form.dcs.data = DCS.query.filter_by(id=pd_edit.dcs_id).first().name
    form.pro.data = Project.query.filter_by(id=pd_edit.project_id).first().name
    form.sys.data = Subsystem.query.filter_by(id=pd_edit.sys_id).first().name
    form.hmi.data = HmiMode.query.filter_by(id=pd_edit.hmi_id).first().name
    form.cfg.data = ConfigMode.query.filter_by(id=pd_edit.cfg_id).first().name
    form.out.data = pd_edit.pro_out
    return render_template('rk_manage/edit_dcs_project.html', form=form)

# 显示工程
@rk_manage.route('/showprojects', methods=['GET', 'POST'])
@rkuser_required
@login_required
def show_project():
    pros = get_cur_user_pros()
    form = ProjectFilterForm()
    form.pro.choices = [('全部', '全部')]
    form.pro.choices += [(r.name, r.name) for r in pros]
    if form.validate_on_submit():
        if form.pro.data == '全部':
            return render_template('rk_manage/show_project.html', projects=pros, form=form)
        proSelect = Project.query.filter_by(name=form.pro.data)
        return render_template('rk_manage/show_project.html', projects=proSelect, form=form)
    return render_template('rk_manage/show_project.html', projects=pros, form=form)
        #return redirect(url_for('rk_manage.manage'))

# 显示DCS
@rk_manage.route('/showdcses', methods=['GET', 'POST'])
@rkuser_required
@login_required
def show_dcs():
    dcs = get_cur_user_dcses()
    for d in dcs:
        if d.author_id:
            d.alg_keeper = User.query.filter_by(id=d.author_id).first().username
    form = DcsFilterForm()
    form.dcs.choices = [('全部', '全部')]
    form.dcs.choices += [(r.name, r.name) for r in dcs]
    if form.validate_on_submit():
        if form.dcs.data == '全部':
            return render_template('rk_manage/show_dcs.html', dcses=dcs, form=form)
        dcsSelect = DCS.query.filter_by(name=form.dcs.data).first()
        if dcsSelect.author_id:
            dcsSelect.alg_keeper = User.query.filter_by(id=dcsSelect.author_id).first().username
        return render_template('rk_manage/show_dcs.html', dcses=[dcsSelect], form=form)
    return render_template('rk_manage/show_dcs.html', dcses=dcs, form=form)
        #return redirect(url_for('rk_manage.manage'))


# 显示DCS和工程关系
@rk_manage.route('/showrelations', methods=['GET', 'POST'])
@rkuser_required
@login_required
def show_relations():
    sql = MySQL_Utils()
    sqlstr = "SELECT * FROM view_dcs_project vdp WHERE vdp.dcsname is not null AND vdp.projectname is not null"
    pros = Project.query.all()
    dcs = get_cur_user_dcses()
    form = RelFilterForm()
    form.pro.choices = [('全部', '全部')]
    form.pro.choices += [(r.name, r.name) for r in pros]
    form.dcs.choices = [('全部', '全部')]
    form.dcs.choices += [(r.name, r.name) for r in dcs]
    if form.validate_on_submit():
        if form.pro.data != '全部':
            sqlstr += " AND vdp.projectname='%s'" % form.pro.data
        if form.dcs.data != '全部':
            sqlstr += " AND vdp.dcsname='%s'" % form.dcs.data
        result = sql.exec_sql(sqlstr)
        relations = get_cur_user_dcs2pros(list(result))
        return render_template('rk_manage/show_relations.html', rels=relations, form=form)
    result = sql.exec_sql(sqlstr)
    relations = get_cur_user_dcs2pros(list(result))
    return render_template('rk_manage/show_relations.html', rels=relations, form=form)

# 显示工程和DCS关系
@rk_manage.route('/showrelations/pro2dcs', methods=['GET', 'POST'])
@rkuser_required
@login_required
def show_relations_pd():
    sql = MySQL_Utils()
    sqlstr = "SELECT * FROM view_project_dcs vpd WHERE vpd.dcsname is not null AND vpd.projectname is not null"
    pros = get_cur_user_pros()
    dcs = DCS.query.all()
    form = RelFilterForm()
    form.pro.choices = [('全部', '全部')]
    form.pro.choices += [(r.name, r.name) for r in pros]
    form.dcs.choices = [('全部', '全部')]
    form.dcs.choices += [(r.name, r.name) for r in dcs]
    if form.validate_on_submit():
        if form.pro.data != '全部':
            sqlstr += " AND vpd.projectname='%s'" % form.pro.data
        if form.dcs.data != '全部':
            sqlstr += " AND vpd.dcsname='%s'" % form.dcs.data
        result = sql.exec_sql(sqlstr)
        relations = get_cur_user_pro2dcses(list(result))

        return render_template('rk_manage/show_relations_pd.html', rels=relations, form=form)
    result = sql.exec_sql(sqlstr)
    relations = get_cur_user_pro2dcses(list(result))
    return render_template('rk_manage/show_relations_pd.html', rels=relations, form=form)


@rk_manage.route('/download/file/<string:filename>', methods=['GET'])
@rkuser_required
@login_required
def download_file(filename):
    if request.method == "GET":
        if os.path.isfile(os.path.join('app\\_uploads', filename)):
            return send_from_directory(directory='_uploads', filename=filename, as_attachment=True)
        abort(404)

# 初始化
@rk_manage.route('/initial', methods=['GET', 'POST'])
@admin_required
@login_required
def initial():
    form = InitForm()
    if form.validate_on_submit():
        if form.file_mdb.data:
            access = AccessHelper(form.file_mdb.data.filename)
            sql = 'SELECT * FROM 控制公司'
            data = access.select(sql)

        if form.file_excel.data:
            pass

        return redirect(url_for('rk_manage/manage.html'))
    return render_template('rk_manage/init_mdb.html', form=form)

def get_cur_user_pros():
    if current_user.is_administrator():
        pros = Project.query.all()
    else:
        pros = Project.query.filter_by(author_id=current_user.id)
    return pros

def get_cur_user_pro2dcses(relations):
    pros = get_cur_user_pros()
    list = []
    for pro in pros:
        list.append(pro.name)
    new_relas = []
    for rela in relations:
        if rela['projectname'] in list:
            new_relas.append(rela)
    return new_relas

def get_cur_user_dcses():
    if current_user.is_administrator():
        dcs = DCS.query.all()
    else:
        dcs = DCS.query.filter_by(author_id=current_user.id)
    return dcs

def get_cur_user_dcs2pros(relations):
    dcses = get_cur_user_dcses()
    list = []
    for dcs in dcses:
        list.append(dcs.name)
    new_relas = []
    for rela in relations:
        if rela['dcsname'] in list:
            new_relas.append(rela)
    return new_relas