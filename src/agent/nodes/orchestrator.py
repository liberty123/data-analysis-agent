#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from src.agent.schema import DATABASE_SCHEMA
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage, HumanMessage
from src.agent.state import Agentstate
from src.agent.llm import llm
from src.agent.nodes import sys_prompt
# from src.agent.tools import tools


system_prompt = sys_prompt["system"] + f"可用的数据库表结构如下：{DATABASE_SCHEMA}。请根据用户问题和表结构生成执行计划。"
# llm_with_tools = llm.bind_tools(tools=tools)


def chat(state: Agentstate, content: str) -> Agentstate:
    state["plan"] = []
    state["final_answer"] = content
    state["can_return"] = True
    return state


def Agent(state: Agentstate):
    messages = list(state['messages'])

    if len(messages) == 1 and isinstance(messages[0], HumanMessage):
        state["user_input"] = messages[0].content
    messages = [SystemMessage(content=system_prompt)] + messages

    response = llm.invoke(messages)
    json_response_content = json.loads(response.content)
    try:
        state["plan"] = json_response_content["steps"]
        if len(state["plan"]) == 0:
            return chat(state, json_response_content["response"])
    except (json.JSONDecodeError, KeyError):
        return chat(state, json_response_content["response"])
    state["current_step"] = 0
    state["retry_count"] = 0
    state["step_results"] = []
    state["messages"].append(response)
    return state
