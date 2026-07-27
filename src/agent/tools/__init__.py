#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.agent.tools.sql_query import sql_query

tools = [sql_query]
tools_dict = {tool.name: tool for tool in tools}