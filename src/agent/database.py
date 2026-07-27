#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/7/23 18:18
# @Author  : name
# @File    : database.py
from dbutils.pooled_db import PooledDB
from pymysql.cursors import DictCursor
import pymysql


# 建立连接
_pool = PooledDB(
    creator=pymysql,  # 使用 PyMySQL
    maxconnections=10,  # 最多 10 个连接
    mincached=2,  # 空闲时保留 2 个
    maxcached=5,  # 最多缓存 5 个
    blocking=True,  # 连接耗尽时等待而不是报错
    host='localhost',
    user='root',
    password='',
    database='agent',
    charset='utf8mb4',
    cursorclass=DictCursor
)


def get_connection():
    """从连接池获取一个连接（线程安全）"""
    return _pool.connection()
