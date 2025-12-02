from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

from agents.router_agent import route_question
from agents.rag_agent import run_rag_agent
from agents.summary_agent import run_summary_agent
from agents.reasoning_agent_for_his import run_reasoning_agent


class HistoryState(TypedDict):
    question: str
    context: str | None
    answer: str | None


def router_node(state: HistoryState):
    state["type"] = route_question(state["question"])
    return state


def rag_node(state: HistoryState):
    rag = run_rag_agent(state["question"])
    state["context"] = rag["context"]
    state["answer"] = rag["answer"]
    return state


def summary_node(state: HistoryState):
    context = state.get("context", "")
    state["answer"] = run_summary_agent(context, state["question"])
    return state


def reasoning_node(state: HistoryState):
    context = state.get("context", "")
    state["answer"] = run_reasoning_agent(context, state["question"])
    return state


def route_to_agent(state):
    t = state.get("type", "fact")
    if t == "summary":
        return "summary_node"
    if t == "reasoning":
        return "reasoning_node"
    return "rag_node"


builder = StateGraph(HistoryState)

builder.add_node("router_node", router_node)
builder.add_node("rag_node", rag_node)
builder.add_node("summary_node", summary_node)
builder.add_node("reasoning_node", reasoning_node)

builder.set_entry_point("router_node")

builder.add_conditional_edges("router_node", route_to_agent)
builder.add_edge("rag_node", END)
builder.add_edge("summary_node", END)
builder.add_edge("reasoning_node", END)

history_graph = builder.compile()


def run_history_pipeline(question: str):
    init = {"question": question, "context": None, "answer": None}
    final = history_graph.invoke(init)
    return final["answer"]
