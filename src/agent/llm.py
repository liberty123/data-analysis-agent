#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/7/23 18:20
# @Author  : name
# @File    : llm.py
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os

load_dotenv()
llm = ChatOpenAI(
    model="deepseek-v4-pro",  # 或 "deepseek-reasoner"
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
    temperature=0
)


