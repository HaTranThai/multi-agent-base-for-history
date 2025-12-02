# graph/history_graph.py
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END

from agents.router_agent import route_question
from agents.rag_agent import run_rag_agent
from agents.summary_agent import run_summary_agent
from agents.reasoning_agent_for_his import run_reasoning_agent


class HistoryState(TypedDict):
    question: str          # câu cuối cùng user hỏi
    merged_query: str      # câu hỏi đã gộp với history
    history: List[Dict[str, Any]]  # lịch sử hội thoại
    context: str | None
    answer: str | None
    type: str | None       # fact / summary / reasoning


def build_merged_query(question: str, history: List[Dict[str, Any]]) -> str:
    """
    Gộp lịch sử hội thoại vào query mới để RAG hiểu 'phong trào đó' là gì.
    """
    if not history:
        return question

    # Lấy câu hỏi gần nhất và tóm tắt ngắn gọn từ câu trả lời
    last_turn = history[-1]
    last_q = last_turn['question']
    last_a = last_turn['answer']
    
    # Lấy các từ khóa quan trọng từ câu trả lời trước (50 từ đầu)
    summary = ' '.join(last_a.split()[:50]) + '...' if len(last_a.split()) > 50 else last_a
    
    return f"Ngữ cảnh: {last_q} - {summary}\n\nCâu hỏi tiếp theo: {question}"


def router_node(state: HistoryState) -> HistoryState:
    state["type"] = route_question(state["question"])
    print("=== ROUTER CHỌN:", state["type"])
    return state


def rag_node(state: HistoryState) -> HistoryState:
    # dùng merged_query (có history) chứ không phải câu hỏi thô
    rag = run_rag_agent(state["merged_query"])
    state["context"] = rag["context"]
    state["answer"] = rag["answer"]
    return state


def summary_node(state: HistoryState) -> HistoryState:
    ctx = state.get("context") or ""
    state["answer"] = run_summary_agent(ctx, state["question"])
    return state


def reasoning_node(state: HistoryState) -> HistoryState:
    ctx = state.get("context") or ""
    # Nếu không có context từ RAG, dùng history để tạo context
    if not ctx and state.get("history"):
        last_turn = state["history"][-1]
        ctx = f"Câu hỏi trước: {last_turn['question']}\nTrả lời: {last_turn['answer']}"
    state["answer"] = run_reasoning_agent(ctx, state["question"])
    return state


def route_to_agent(state: HistoryState) -> str:
    t = (state.get("type") or "fact").lower()
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


def run_history_pipeline(question: str, history: List[Dict[str, Any]]) -> str:
    merged_query = build_merged_query(question, history)
    init: HistoryState = {
        "question": question,
        "merged_query": merged_query,
        "history": history,
        "context": None,
        "answer": None,
        "type": None,
    }
    final = history_graph.invoke(init)
    return final["answer"]
