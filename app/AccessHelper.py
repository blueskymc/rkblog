#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' Access module '

__author__ = 'Ma Cong'

"""
func: 基于pypyodbc的Access数据库交互类
"""

import pypyodbc

class AccessHelper():
    def __init__(self, path):
        str = u'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + path
        self.conn = pypyodbc.win_connect_mdb(str)

    def select(self, sql):
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
            return cur.fetchall()
        except:
            return []