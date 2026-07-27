#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from src.agent.state import Agentstate
from src.agent.tools import tools_dict
from langchain_core.messages import AIMessage


def executor(state: Agentstate) -> Agentstate:

    plan = state["plan"]
    for step in plan:
        if step['tool_name'] in tools_dict:
            result = tools_dict[step['tool_name']].invoke(step['tool_args'])
            step_results = {"step_id": step["step_id"], "result": result}
            state["step_results"].append(step_results)
        else:
            step_results = {"step_id": step["step_id"], "result": "错误：找不到该工具"}
            state["step_results"].append(step_results)
    return state
