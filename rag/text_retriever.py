from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

INDEX_DIR = "text_faiss_index"

def get_text_retriever(k: int = 5):
    embeddings = OpenAIEmbeddings()
    vectordb = FAISS.load_local(
        INDEX_DIR,
        embeddings,
        allow_dangerous_deserialization=True,
    )
    return vectordb.as_retriever(search_kwargs={"k": k})
