#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' loader module '

__author__ = 'Ma Cong'

"""
func: 基于pymysql的数据库交互类，支持事务提交和回滚，返回结果记录行数，和insert的最新id
"""

import pymysql
from warnings import filterwarnings
from config import config

filterwarnings('ignore', category=pymysql.Warning)
CONNECT_TIMEOUT = 100
IP = 'localhost'
PORT = 3306
USER = 'root'
PASSSWORD = config['development'].MYSQL_PASSWORD

class QueryException(Exception):
    """
    """

class ConnectionException(Exception):
    """
    """

class MySQL_Utils():
    def __init__(
            self, ip=IP, port=PORT, user=USER, password=PASSSWORD,
            connect_timeout=CONNECT_TIMEOUT, remote=False, socket='', dbname='rk_blog'):
        self.__conn = None
        self.__cursor = None
        self.lastrowid = None
        self.connect_timeout = connect_timeout
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.mysocket = socket
        self.remote = remote
        self.db = dbname
        self.rows_affected = 0

        self.__init_conn()

    def __init_conn(self):
        try:
            conn = pymysql.connect(
                host=self.ip,
                port=int(self.port),
                user=self.user,
                passwd=self.password,
                db=self.db,
                connect_timeout=self.connect_timeout,
                charset='utf8', unix_socket=self.mysocket)
        except pymysql.Error as e:
            raise ConnectionException(e)
        self.__conn = conn
        self.con = conn

    def __init_cursor(self):
        if self.__conn:
            self.__cursor = self.__conn.cursor(pymysql.cursors.DictCursor)

    def close(self):
        if self.__conn:
            self.__conn.close()
            self.__conn = None

    # 专门处理select 语句
    def exec_sql(self, sql, args=None):
        try:
            if self.__conn is None:
                self.__init_conn()
                self.__init_cursor()
            if self.__cursor is None:
                self.__init_cursor()
            self.__conn.autocommit = True
            self.__cursor.execute(sql, args)
            self.commit()
            self.rows_affected = self.__cursor.rowcount
            results = self.__cursor.fetchall()
            return results

        except pymysql.Error as e:
            print(sql)
            raise pymysql.Error(e)

        finally:
            if self.__conn:
                self.close()

    # 专门处理dml语句 delete，updete，insert
    def exec_txsql(self, sql, args=None):
        try:
            if self.__conn is None:
                self.__init_conn()
                self.__init_cursor()
            if self.__cursor is None:
                self.__init_cursor()
            self.rows_affected = self.__cursor.execute(sql, args)
            self.commit()
            self.lastrowid = self.__cursor.lastrowid
            return self.rows_affected

        except pymysql.Error as e:
            raise pymysql.Error(e)

        finally:
            if self.__conn:
                self.close()
            #if self.__cursor:
                #self.__cursor.close()
                #self.__cursor = None

    # 提交
    def commit(self):
        try:
            if self.__conn:
                self.__conn.commit()

        except pymysql.Error as e:
            raise pymysql.Error(e)

        finally:
            if self.__conn:
                self.close()

    # 回滚操作
    def rollback(self):
        try:
            if self.__conn:
                self.__conn.rollback()
        except pymysql.Error as e:
            raise pymysql.Error(e)

        finally:
            if self.__conn:
                self.close()

    # 适用于需要获取插入记录的主键自增id
    def get_lastrowid(self):
        return self.lastrowid

    # 获取dml操作影响的行数
    def get_affectrows(self):
        return self.rows_affected

    # MySQL_Utils初始化的实例销毁之后，自动提交
    def __del__(self):
        self.commit()