#!/usr/bin/env python
# -*- coding: utf-8 -*-
from langchain_core.tools import tool
from src.agent.database import get_connection


@tool
def sql_query(sql: str) -> list[str]:
    """这是一个执行SQL语句的函数，将返回sql语句执行结果
    参数：
        sql: SQL语句
    """
    # 执行查询
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()
    except Exception as e:
        return f"error: SQL 执行错误：{e}。请修正 SQL 后重试。"
    finally:
        conn.close()  # 归还连接到池，而不是真正关闭 TCP

@tool
def search_csv(sql: str) -> str:
    """这是一个再csv中进行查询的方法
    参数：
        sql: SQL语句
    """
    return ""