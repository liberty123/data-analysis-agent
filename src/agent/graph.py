from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from src.agent.state import Agentstate
from src.agent.nodes.router import should_continue
from src.agent.nodes.orchestrator import Agent
from src.agent.tools import tools
from langgraph.checkpoint.memory import MemorySaver
from src.agent.nodes.executor import executor
from src.agent.nodes.report import report_node
from src.agent.nodes.observer import observer_node
from src.agent.nodes.router import error_rout, observer_rout, plan_router

memory = MemorySaver()


graph = StateGraph(Agentstate)
graph.add_node("our_agent", Agent)
graph.add_node("executor", executor)
graph.add_node("report", report_node)
graph.add_node("observer", observer_node)

graph.add_edge(START, "our_agent")
graph.add_conditional_edges(
      "our_agent",
      plan_router,
      {
          "execute": "executor",
          "end": END
      }
  )

graph.add_conditional_edges(
    "executor",
    error_rout,
    {
        "fix_sql": "our_agent",
        "report": "report",
        "END": END,
    }
)
graph.add_edge("report", "observer")
graph.add_conditional_edges(
    "observer",
    observer_rout,
    {
        True: END,
        False: "our_agent"
    }
)

app = graph.compile(checkpointer=memory)




