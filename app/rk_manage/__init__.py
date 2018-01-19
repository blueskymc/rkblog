#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
定义 热控管理 模块
"""

___author__ = 'MaCong'

from flask import Blueprint

rk_manage = Blueprint('rk_manage', __name__)

from . import views