#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from src.agent.state import Agentstate
from src.agent.llm import llm
from src.agent.nodes import report_prompt


def report_node(state: Agentstate) -> Agentstate:
    """
    这个节点将sql的查询结果，转为文字描述，进行总结生成报告
    """
    messages = report_prompt["report_prompt"].format(
        user_question=state["user_input"],
        plan=state["plan"],
        result=state["step_results"]
    )
    response = llm.invoke([messages])
    state["messages"].append(response)
    state["final_answer"] = response.content
    return state
