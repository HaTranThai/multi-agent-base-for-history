# rag/build_multi_text_index.py
import os
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

DATA_DIR = "data"
INDEX_DIR = "multi_text_faiss_index"


def build_multi_text_index():
    docs = []
    for filename in os.listdir(DATA_DIR):
        if not filename.endswith(".txt"):
            continue
        path = os.path.join(DATA_DIR, filename)
        print(f"📄 Loading {path}")
        loader = TextLoader(path, encoding="utf-8")
        
        file_docs = loader.load()
        for d in file_docs:
            d.metadata["source"] = filename
        docs.extend(file_docs)

    print(f"Loaded {len(docs)} documents")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " "],
    )
    split_docs = splitter.split_documents(docs)
    print(f"Split into {len(split_docs)} chunks")

    embeddings = OpenAIEmbeddings()
    vectordb = FAISS.from_documents(split_docs, embeddings)
    vectordb.save_local(INDEX_DIR)
    print(f"✅ Saved FAISS index to {INDEX_DIR}")


if __name__ == "__main__":
    build_multi_text_index()
