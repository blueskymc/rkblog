#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
入口
"""

___author__ = 'MaCong'

import os
from app import create_app, db
from app.models import User, Blog, Comment, Label
from flask_script import Manager, Shell

app = create_app(os.getenv('FLASK_CONFIG') or 'default')   # os.getenv('FLASK_CONFIG') or 'default'
manager = Manager(app)

def make_shell_context():
    return dict(app=app, db=db, User=User, Blog=Blog, Comment=Comment, Label=Label)
manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()