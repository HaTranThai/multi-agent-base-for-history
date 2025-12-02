from agents.base_llm import llm_1
from langchain_core.prompts import ChatPromptTemplate

summary_prompt = ChatPromptTemplate.from_messages([
    ("system", "Hãy tóm tắt đoạn lịch sử sau rõ ràng và ngắn gọn:\n{context}"),
    ("human", "{question}")
])

summary_chain = summary_prompt | llm_1

def run_summary_agent(context: str, question: str):
    res = summary_chain.invoke({"context": context, "question": question})
    return res.content
