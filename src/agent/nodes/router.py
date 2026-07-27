#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.agent.state import Agentstate
from src.agent.tools import tools_dict


def should_continue(state: Agentstate) -> str:
    messages = state["messages"]
    last_messages = messages[-1]
    if not last_messages.tool_calls:
        return "END"
    else:
        return "continue"


def error_rout(state: Agentstate) -> str:
    for r in state["step_results"]:
        result_str = str(r.get("result", ""))
        if "error" in result_str:
            return "fix_sql"
    if len(state["step_results"]) > 0:
        return "report"
    return "END"


def observer_rout(state: Agentstate) -> bool:
    return state["can_return"]


def plan_router(state: Agentstate) -> str:
    plan = state.get("plan", [])

    if not plan:
        # 空 plan → LLM 可能直接回答了，或者需要反问用户
        return "end"

    # 检查 plan 里有没有"澄清"类型的步骤（需要反问用户）
    for step in plan:
        if step.get("tool_name") in ("clarify", "ask_user"):
            return "end"

    # 检查 plan 里有没有需要工具执行的步骤
    has_tool_step = any(
        step.get("tool_name") in tools_dict for step in plan
    )

    if has_tool_step:
        return "execute"
    else:
        # plan 里没有可执行工具 → 可能是纯对话回复
        return "end"