from rag.text_retriever import get_text_retriever
from agents.base_llm import llm_1
from langchain_core.prompts import ChatPromptTemplate

retriever = get_text_retriever(k=5)

rag_prompt = ChatPromptTemplate.from_messages([
    ("system", "Dựa vào đoạn lịch sử dưới đây, trả lời câu hỏi của người dùng.\n\n{context}"),
    ("human", "{question}")
])

rag_chain = rag_prompt | llm_1

def run_rag_agent(question: str):
    docs = retriever.invoke(question)
    context = "\n\n".join([d.page_content for d in docs])
    res = rag_chain.invoke({"context": context, "question": question})
    return {"answer": res.content, "context": context}
