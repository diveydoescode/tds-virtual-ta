# 🤖 TDS Virtual TA

**TDS Virtual TA** is an AI-powered assistant that automatically answers student queries for the IIT Madras course _Tools in Data Science (TDS)_, using:

- 📚 Official course content (`coursecontent.md`)
- 🧵 Student discussions from Discourse
- 🧠 GPT-4o-mini via IITM's AI Proxy

> Built with ❤️ by an IITM student, for IITM students.

---

## 🚀 Features

- ✅ Answers realistic student queries using course + forum data
- 🔍 Semantic search over scraped Discourse + structured syllabus
- 💬 Uses GPT-4o-mini (or gpt-3.5) to generate answers
- 🔗 Returns helpful links to source threads
- 📦 API-ready with JavaScript

---

## 📁 Project Structure

```
tds-virtual-ta/
├── main.js            # Node.js app (serves /api/)
├── scrape_discourse.js # Scrapes Discourse threads
├── coursecontent.md    # Official course syllabus (downloaded)
├── parse_coursecontent.js # Converts markdown to structured JSON
├── build_knowledge_chunks.js # Merges and cleans all content into Q/A chunks
├── generate_embeddings.js # Generates OpenAI embeddings using AI Proxy
├── embeddings.jsonl    # Final indexed content with embeddings
├── package.json        # JavaScript dependencies
├── .env.example        # Template for environment config
├── discourse_data/    # Scraped raw discourse topic JSONs
└── coursecontent_structured.jsonl
```

---

## ⚙️ Setup Instructions

### 1. Clone this repo
```bash
git clone https://github.com/YOUR_USERNAME/tds-virtual-ta.git
cd tds-virtual-ta
```

### 2. Install dependencies
```bash
npm install
```

### 3. Setup .env
Create a file called .env based on .env.example:

```
OPENAI_API_BASE=https://aiproxy.sanand.workers.dev/openai/v1
OPENAI_API_KEY=your_token_here
OPENAI_MODEL=gpt-4o-mini
```

### 4. Start the API
```bash
npm start
```

Visit: `http://localhost:3000/api/` to test the API!

---

## 📡 API Usage

**Endpoint**
```
POST /api/
```

**Example Request**
```json
{
  "question": "Should I use GPT-4o or GPT-3.5 for GA5?"
}
```

**Example Response**
```json
{
  "answer": "You must use gpt-3.5-turbo-0125...",
  "links": [
    {
      "url": "https://discourse.onlinedegree.iitm.ac.in/t/155939",
      "text": "GA5 Model Clarification"
    }
  ]
}
```

---

## 📤 Deployment Options

**▶️ Option 1: Local with ngrok**
```bash
ngrok http 3000
```

**▶️ Option 2: Deploy to Render or Replit**
- Set `npm start` as start command
- Add `.env` variables in settings

---

## ✅ Evaluation Criteria (Passed)

- ✅ Scrapes course and forum data
- ✅ Exposes API endpoint
- ✅ Uses GPT via AI Proxy
- ✅ Answers real-world TDS queries
- ✅ Returns useful source links
- ✅ Public GitHub + MIT License

---

## 📜 License

MIT License © 2025

---

## 🙌 Acknowledgements

- OpenAI
- IITM Online Degree Team
- s-anand / TDS course
