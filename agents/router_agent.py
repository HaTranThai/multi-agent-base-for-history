from agents.base_llm import llm_1
from langchain_core.prompts import ChatPromptTemplate

router_prompt = ChatPromptTemplate.from_messages([
    ("system", """
Bạn là router phân loại câu hỏi của người dùng về lịch sử.
Các loại:
- fact: câu hỏi thông tin đơn giản
- summary: yêu cầu tóm tắt
- reasoning: phân tích nguyên nhân – hệ quả – đánh giá

Chỉ trả về 1 trong 3 từ: fact, summary, reasoning.
    """),
    ("human", "{question}")
])

router_chain = router_prompt | llm_1

def route_question(question: str):
    res = router_chain.invoke({"question": question})
    output = res.content.strip().lower()
    if output not in ["fact", "summary", "reasoning"]:
        return "fact"
    return output
