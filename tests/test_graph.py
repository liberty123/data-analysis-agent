#!/usr/bin/env python
# -*- coding: utf-8 -*-
from langchain_core.messages import HumanMessage
from src.agent.graph import app


def running_agent():
    print("\n=== SQL AGENT ===")

    while True:
        user_input = input("\nWhat is your question: ")
        if user_input.lower() in ['exit', 'quit']:
            break

        messages = [HumanMessage(content=user_input)]  # converts back to a HumanMessage type
        config = {"configurable": {"thread_id": "test"}}
        result = app.invoke({"messages": messages}, config=config)

        print("\n=== ANSWER ===")
        print(result["final_answer"])


running_agent()
