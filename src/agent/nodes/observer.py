#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from src.agent.state import Agentstate
from src.agent.llm import llm
from src.agent.nodes import observer_prompt


def observer_node(state: Agentstate) -> Agentstate:
    """
    这个节点将判断返回结果，决定是否可以回答用户的问题，是否结束循环
    """
    messages = observer_prompt["observer_prompt"].format(
        user_question=state["user_input"],
        data_summary=state["final_answer"]
    )
    response = llm.invoke([messages])
    response_content = json.loads(response.content)
    state["can_return"] = response_content["can_return"]
    state["observer_feedback"] = response_content["feedback"]
    state["final_confidence"] = response_content["confidence"]
    state["messages"].append(response)
    return state
