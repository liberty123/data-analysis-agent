#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/7/23 18:51
# @Author  : name
# @File    : test_fastapi.py

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.server.app:fastapi_app",          # 你的 FastAPI 实例路径
        host="0.0.0.0",
        port=8080,
        reload=True          # 开发模式热重载
    )