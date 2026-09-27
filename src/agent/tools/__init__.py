#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.agent.tools.sql_query import sql_query
from src.agent.tools.python_exec import execute_python_code

tools = [sql_query, execute_python_code]
tools_dict = {tool.name: tool for tool in tools}