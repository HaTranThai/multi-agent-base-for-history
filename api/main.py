# api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any

from graph.history_graph import run_history_pipeline

app = FastAPI(
    title="Multi-Agent RAG API",
    description="",
    version="0.1.0",
)

class Query(BaseModel):
    question: str

@app.post("/history-qa")
async def history_qa(q: Query):
    answer = run_history_pipeline(q.question)
    return {"question": q.question, "answer": answer}