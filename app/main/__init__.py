#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
定义 main 模块
"""

___author__ = 'MaCong'

from flask import Blueprint

main = Blueprint('main', __name__)

from . import views