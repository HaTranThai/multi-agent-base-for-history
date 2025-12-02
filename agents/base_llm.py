# agents/base_llm.py
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm_1 = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7
)
