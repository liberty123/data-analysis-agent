#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


class QueryRequest(BaseModel):
    session_id: str
    question: str


class QueryResponse(BaseModel):
    answer: str


# 创建应用实例
fastapi_app = FastAPI()

# 挂载前端静态文件
static_dir = Path(__file__).parent.parent.parent / "static"
fastapi_app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

from src.server.routes import chat, health
