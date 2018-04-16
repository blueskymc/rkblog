#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
定义 app 模块
"""

___author__ = 'MaCong'

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_login import LoginManager
from flask_mail import Mail
from flask_babel import Babel
from flask_pagedown import PageDown
from flask_uploads import UploadSet, configure_uploads, patch_request_class, DEFAULTS, ARCHIVES
from config import config


bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
mail = Mail()
babel = Babel()
pagedown = PageDown()
uploadset = UploadSet('files', DEFAULTS + ARCHIVES)
uploadset_csv = UploadSet('csv', tuple('csv xls xlsx'.split()))
uploadset_mdb = UploadSet('mdb', tuple('mdb mb'.split()))
abs_upload_path = ''

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'main.index'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.config['UPLOADED_FILES_DEST'] = 'app\\_uploads\\'
    configure_uploads(app, uploadset)
    patch_request_class(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app)
    pagedown.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .manage import manage as manage_blueprint
    app.register_blueprint(manage_blueprint, url_prefix='/manage')

    from .rk_manage import rk_manage as rk_manage_blueprint
    app.register_blueprint(rk_manage_blueprint, url_prefix='/rk_manage')

    return app