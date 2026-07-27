#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.server.app import fastapi_app, QueryRequest, QueryResponse
from langchain_core.messages import HumanMessage
from fastapi import HTTPException
from src.agent.graph import app


@fastapi_app.post("/rag/ask", response_model=QueryResponse)
def ask_rag(query: QueryRequest):
    config = {"configurable": {"thread_id": query.session_id}}
    try:
        # 调用你的 Agent
        result = app.invoke({"messages": [HumanMessage(content=query.question)]}, config=config)
        answer = result["messages"][-1].content
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))