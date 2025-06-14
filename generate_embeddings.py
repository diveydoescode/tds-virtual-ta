import os
import json
import time
import requests
from dotenv import load_dotenv

# Load your .env containing AIPROXY keys
load_dotenv()

API_BASE = os.getenv("OPENAI_API_BASE").rstrip("/")
API_KEY = os.getenv("OPENAI_API_KEY")
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

MODEL = "text-embedding-3-small"
INPUT_FILE = "knowledge_chunks.jsonl"
OUTPUT_JSONL = "embeddings.jsonl"
OPTIONAL_PRETTY_JSON = "embeddings_preview.json"

def get_embedding(text):
    response = requests.post(
        f"{API_BASE}/embeddings",
        headers=HEADERS,
        json={"model": MODEL, "input": text}
    )
    if response.status_code == 200:
        return response.json()["data"][0]["embedding"]
    else:
        print(f"❌ {response.status_code} Error: {response.text[:200]}")
        return None

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input file {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as fin:
        chunks = [json.loads(line) for line in fin]

    embedded_chunks = []
    with open(OUTPUT_JSONL, "w", encoding="utf-8") as fout:
        for i, chunk in enumerate(chunks, 1):
            text = chunk["content"]
            embedding = get_embedding(text)

            if embedding:
                chunk["embedding"] = embedding
                json.dump(chunk, fout)
                fout.write("\n")

                # Optional preview log
                preview = text[:60].replace("\n", " ") + ("..." if len(text) > 60 else "")
                print(f"✅ {i}/{len(chunks)} embedded → {chunk['title'][:40]} | Preview: {preview}")
                embedded_chunks.append({
                    "title": chunk.get("title"),
                    "source": chunk.get("source"),
                    "url": chunk.get("url", ""),
                    "content": preview,
                    "embedding_preview": embedding[:5]  # just first 5 values
                })
            else:
                print(f"⚠️ {i}/{len(chunks)} FAILED → {chunk['title'][:40]}")

            time.sleep(1.5)  # to respect AI Proxy rate limits

    # Save a human-friendly JSON preview
    with open(OPTIONAL_PRETTY_JSON, "w", encoding="utf-8") as f:
        json.dump(embedded_chunks, f, indent=2, ensure_ascii=False)

    print(f"\n🎉 Done! {len(embedded_chunks)} embeddings written to {OUTPUT_JSONL}")
    print(f"👀 Preview available in {OPTIONAL_PRETTY_JSON}")

if __name__ == "__main__":
    main()
