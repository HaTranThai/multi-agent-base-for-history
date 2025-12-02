from agents.base_llm import llm_1
from langchain_core.prompts import ChatPromptTemplate

reason_prompt = ChatPromptTemplate.from_messages([
    ("system", """
Bạn là chuyên gia lịch sử.
Dựa trên đoạn văn dưới đây, hãy phân tích sâu:
- Nguyên nhân
- Ý nghĩa
- Hệ quả
- Bối cảnh lịch sử
- Nhận xét của bạn

ĐOẠN VĂN:
{context}
    """),
    ("human", "{question}")
])

reason_chain = reason_prompt | llm_1

def run_reasoning_agent(context: str, question: str):
    res = reason_chain.invoke({"context": context, "question": question})
    return res.content
