# api/main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from pydantic import BaseModel
from typing import List, Dict, Any

from graph.history_graph import run_history_pipeline
from memory.store import get_history, add_turn

app = FastAPI(
    title="Multi-Agent History QA",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # hoặc ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    session_id: str
    question: str


@app.post("/history-qa")
async def history_qa(q: Query):
    # 1. lấy history
    history: List[Dict[str, Any]] = get_history(q.session_id)

    # 2. chạy graph với history
    answer = run_history_pipeline(q.question, history)

    # 3. lưu lại lượt hỏi–đáp mới
    add_turn(q.session_id, q.question, answer)

    # 4. trả về kèm history mới (lấy từ store sau khi đã lưu)
    new_history = get_history(q.session_id)
    return {
        "session_id": q.session_id,
        "question": q.question,
        "answer": answer,
        "history": new_history,
    }
