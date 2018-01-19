#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
定义 author 模块
"""

___author__ = 'MaCong'

from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views