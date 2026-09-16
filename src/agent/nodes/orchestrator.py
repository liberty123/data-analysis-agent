#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from src.agent.schema import DATABASE_SCHEMA
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage, HumanMessage
from src.agent.state import Agentstate
from src.agent.llm import llm
from src.agent.nodes import sys_prompt
import re
# from src.agent.tools import tools


system_prompt = sys_prompt["system"] + f"可用的数据库表结构如下：{DATABASE_SCHEMA}。请根据用户问题和表结构生成执行计划。"
# llm_with_tools = llm.bind_tools(tools=tools)


def chat(state: Agentstate, content: str) -> Agentstate:
    state["plan"] = []
    state["final_answer"] = content
    state["can_return"] = True
    return state


def _parse_json(text: str):
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if m:
        text = m.group(1).strip()
    return json.loads(text)

def Agent(state: Agentstate):
    messages = list(state['messages'])

    if len(messages) == 1 and isinstance(messages[0], HumanMessage):
        state["user_input"] = messages[0].content
    messages = [SystemMessage(content=system_prompt)] + messages
    error_str = ""
    state["step_results"] = []
    for i in state['step_results']:
        if "error" in i["result"]:
            error_str += i["result"]
    if error_str != "":
        messages += [HumanMessage(content=error_str)]

    response = llm.invoke(messages)
    json_response_content = _parse_json(response.content)
    try:
        state["plan"] = json_response_content["steps"]
        if len(state["plan"]) == 0 or state["plan"][0]["tool_name"] == "clarify":
            return chat(state, json_response_content["response"])
    except (json.JSONDecodeError, KeyError):
        return chat(state, json_response_content["response"])
    state["current_step"] = 0
    state["retry_count"] = 0
    state["step_results"] = []
    state["messages"].append(response)
    return state
