# 📚 AI Tutor for State Board Students

An intelligent tutoring system that ingests state-board textbook PDFs and answers student questions using **Context Pruning** — sending only the most relevant chapters to the LLM, reducing API costs by up to 80%.

Built for rural India where internet is limited and API costs must be minimal.

---

## 🚀 Features

- **PDF Ingestion** — Upload any state-board textbook PDF; it is automatically chunked and indexed using FAISS
- **Context Pruning** — Instead of sending the entire book to the LLM, only the top 3 most relevant chapters are kept; then only the best 5–8 chunks are sent — dramatically reducing token usage
- **Gemini 2.5 Flash** — Uses Google's fast, low-cost Gemini model for answers
- **Offline Embeddings** — Uses `sentence-transformers/all-MiniLM-L6-v2` locally (no API cost for search)
- **Multi-Book Support** — Upload multiple textbooks; switch between them with one click
- **Delete Books** — Remove any ingested book and re-upload a new one
- **Live Cost Stats** — Every answer shows chapters pruned, chunks sent, tokens used, and exact USD cost per query
- **Beautiful Dark UI** — Clean, responsive single-page web interface served directly from Flask

---

## 🧠 How Context Pruning Works

```
Student Question
      │
      ▼
Embed Question (local, free)
      │
      ▼
Score ALL Chapters by similarity → Keep TOP 3 chapters only  ← Context Pruning
      │
      ▼
Pick TOP 8 chunks from those 3 chapters
      │
      ▼
Send ~8 chunks (not the whole book) to Gemini → Get Answer
```

**Result:** ~80% fewer tokens per query = ~80% cheaper than naive RAG.

---

## 📁 Project Structure

```
AI tutor/
├── app.py            # Flask API server
├── ingest.py         # PDF → chunks → FAISS index
├── retrieval.py      # Context Pruning + chunk retrieval
├── generation.py     # Gemini answer generation
├── config.py         # Settings (model, chunk size, top-K)
├── index.html        # Web UI (served by Flask)
├── requirements.txt  # Python dependencies
├── .env              # Your Gemini API key (never commit this!)
├── uploads/          # Uploaded PDFs (auto-created)
└── index_store/      # FAISS indexes per book (auto-created)
```

---

## ⚙️ Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add your Gemini API key

Create a `.env` file (copy from `.env.example`):

```
GEMINI_API_KEY=your_key_here
```

Get a free key at: https://aistudio.google.com/apikey

### 3. Run the server

```bash
python app.py
```

### 4. Open the app

Go to **http://127.0.0.1:5000** in your browser.

---

## 💡 Usage

1. **Upload** a PDF textbook using the upload panel
2. **Wait** for ingestion (~30–60 seconds depending on book size)
3. **Click** the book name to select it
4. **Type** your question and press Enter
5. **Read** the answer — complete, concise, curriculum-aligned

---

## 💰 Cost Comparison

| Approach | Tokens per Query | Cost per Query |
|---|---|---|
| Naive RAG (full book) | ~50,000+ | ~$0.004 |
| **This system (Context Pruning)** | ~2,000–4,000 | **~$0.0001** |

**~40× cheaper** per query using Context Pruning.

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Backend | Python + Flask |
| PDF Parsing | PyMuPDF (fitz) |
| Embeddings | sentence-transformers (local) |
| Vector Search | FAISS (local) |
| LLM | Google Gemini 2.5 Flash |
| Frontend | HTML + Vanilla CSS + JavaScript |

---

## 📄 License

MIT License — free to use, modify, and distribute.
