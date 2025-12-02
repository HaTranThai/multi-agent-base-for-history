# memory/store.py
from typing import Dict, List, TypedDict

class Turn(TypedDict):
    question: str
    answer: str

# session_id -> list[Turn]
SESSIONS: Dict[str, List[Turn]] = {}


def get_history(session_id: str) -> List[Turn]:
    return SESSIONS.get(session_id, [])


def add_turn(session_id: str, question: str, answer: str) -> None:
    history = SESSIONS.get(session_id, [])
    history.append({"question": question, "answer": answer})
    SESSIONS[session_id] = history
