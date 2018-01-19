#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自定义装饰器 模块
"""

___author__ = 'MaCong'

from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kw):
        if not current_user.is_administrator():
            abort(403)
        return func(*args, **kw)
    return wrapper

def rkuser_required(func):
    @wraps(func)
    def wrapper(*args, **kw):
        if not current_user.is_rkuser():
            abort(403)
        return func(*args, **kw)
    return wrapper
