#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
定义 manage 模块
"""

___author__ = 'MaCong'

from flask import Blueprint

manage = Blueprint('manage', __name__)

from . import views