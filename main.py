import os
import json
import numpy as np
from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
from typing import List

load_dotenv()

# === CONFIG ===
API_BASE = os.getenv("OPENAI_API_BASE").rstrip("/")
API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

EMBEDDINGS_FILE = "embeddings.jsonl"
TOP_K = 3

# === APP ===
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str
    image: str = None  # base64 if needed later

def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def get_embedding(text: str) -> List[float]:
    res = requests.post(
        f"{API_BASE}/embeddings",
        headers=HEADERS,
        json={"model": EMBEDDING_MODEL, "input": text}
    )
    res.raise_for_status()
    return res.json()["data"][0]["embedding"]

def load_embeddings():
    chunks = []
    with open(EMBEDDINGS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            chunks.append(obj)
    return chunks

def find_relevant_chunks(question_embedding, all_chunks, top_k=TOP_K):
    scored = []
    for chunk in all_chunks:
        score = cosine_similarity(question_embedding, chunk["embedding"])
        scored.append((score, chunk))
    scored.sort(reverse=True, key=lambda x: x[0])
    return [chunk for score, chunk in scored[:top_k]]

def generate_answer(question: str, context_chunks: List[dict]) -> str:
    context_text = "\n\n---\n\n".join([c["content"] for c in context_chunks])

    system_msg = "You are a helpful teaching assistant for the IIT Madras Tools in Data Science course. Use the provided content to answer the student query."
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"{context_text}\n\nStudent Question: {question}"}
    ]

    res = requests.post(
        f"{API_BASE}/chat/completions",
        headers=HEADERS,
        json={
            "model": CHAT_MODEL,
            "messages": messages,
            "temperature": 0.5
        }
    )
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"]

@app.post("/api/")
async def virtual_ta(request: QueryRequest):
    try:
        question = request.question
        embedding = get_embedding(question)
        chunks = load_embeddings()
        top_chunks = find_relevant_chunks(embedding, chunks)

        answer = generate_answer(question, top_chunks)

        links = []
        for c in top_chunks:
            if c.get("url"):
                links.append({"url": c["url"], "text": c.get("title", "Link")})

        return {
            "answer": answer.strip(),
            "links": links
        }

    except Exception as e:
        return {"answer": f"❌ Error: {str(e)}", "links": []}

@app.get("/")
async def root():
    return {
        "message": "TDS Virtual TA is running. Use POST /api/ to ask questions."
    }

@app.post("/")
async def root_post():
    return {
        "message": "This is the TDS Virtual TA root. Use POST /api/ for questions."
    }

