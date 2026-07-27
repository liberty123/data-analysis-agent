#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/7/23 18:38
# @Author  : name
# @File    : ping.py
from src.server.app import fastapi_app


@fastapi_app.get("/ping")
def ping():
    return {"status": "Connected"}