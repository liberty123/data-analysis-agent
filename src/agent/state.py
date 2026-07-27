#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import TypedDict, List, Dict, Any, Optional, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


# class Agentstate(TypedDict):
#     messages: Annotated[Sequence[BaseMessage], add_messages]
#     # question: Annotated[Sequence[BaseMessage], add_messages]
#     # query: Annotated[Sequence[BaseMessage], add_messages]
#     # sql_result: Annotated[Sequence[BaseMessage], add_messages]


class Agentstate(TypedDict):
    # ==========================================
    # 1. 输入层 (Input Layer)
    # 职责：存储用户的原始输入和固定上下文
    # 生命周期：整个会话不变
    # ==========================================
    user_input: str                 # 用户原始问题

    # ==========================================
    # 2. 消息层 (Message Layer)
    # 职责：存储对话历史，使用 LangGraph 内置的 add_messages 归约器
    # 生命周期：持续追加
    # ==========================================
    messages: Annotated[List[BaseMessage], add_messages]  # 对话历史

    # ==========================================
    # 3. 执行层 (Execution Layer)
    # 职责：存储当前任务执行过程中的动态数据
    # 生命周期：仅在当前执行周期内有效，任务完成后清空或归档
    # ==========================================
    plan: Optional[List[Dict[str, Any]]]   # 执行计划（步骤列表）
    current_step: int                      # 当前执行到的步骤索引
    step_results: List[Dict[str, Any]]     # 每一步的执行结果
    db_result: Optional[str]               # 数据库查询结果（原始）
    error: Optional[str]                   # 当前错误信息
    retry_count: int                       # 当前任务重试次数

    # ==========================================
    # 4. 输出层 (Output Layer)
    # 职责：存储最终结果和观察者评估
    # 生命周期：任务完成时写入，可用于最终展示
    # ==========================================
    final_answer: Optional[str]            # 最终回答
    can_return: bool                       # 观察者是否通过
    observer_feedback: Optional[str]       # 观察者的反馈
    final_confidence: int                  # 最终结果的置信度