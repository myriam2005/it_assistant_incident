import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

if not api_key:
    raise ValueError("GROQ_API_KEY est absente. Vérifie ton fichier .env.")

llm = ChatGroq(model=model_name, temperature=0, api_key=api_key)

response = llm.invoke("Bonjour, réponds en une phrase : qui es-tu ?")
print(response.content)