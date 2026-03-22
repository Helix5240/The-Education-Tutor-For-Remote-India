"""
ingest.py  –  PDF ingestion + chapter detection + FAISS index building
"""
import os, json, re, pickle
import fitz          # pymupdf
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import config

MODEL = SentenceTransformer("all-MiniLM-L6-v2")   # tiny, fast, offline-friendly

# ── helpers ──────────────────────────────────────────────────────────────────

def extract_text_by_page(pdf_path: str) -> list[dict]:
    """Return list of {page, text} dicts."""
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text").strip()
        if text:
            pages.append({"page": i + 1, "text": text})
    doc.close()
    return pages


def detect_chapters(pages: list[dict]) -> list[dict]:
    """
    Heuristic: a line is a chapter heading if it is short, ALL-CAPS or
    starts with 'Chapter'/'Unit'/'Section', and appears near the top of a page.
    Returns list of {chapter_id, title, start_page}.
    """
    chapter_pattern = re.compile(
        r"^(chapter|unit|section|part)\s*\d+", re.IGNORECASE
    )
    chapters = []
    for p in pages:
        first_lines = p["text"].split("\n")[:4]
        for line in first_lines:
            line = line.strip()
            if not line:
                continue
            if chapter_pattern.match(line) or (len(line) < 80 and line.isupper()):
                chapters.append({
                    "chapter_id": len(chapters),
                    "title": line,
                    "start_page": p["page"]
                })
                break
    # make sure at least one "chapter" exists (whole doc fallback)
    if not chapters:
        chapters = [{"chapter_id": 0, "title": "Full Document", "start_page": 1}]
    return chapters


def assign_pages_to_chapters(pages, chapters):
    """Tag each page dict with the chapter it belongs to."""
    # build start-page boundaries
    boundaries = [(c["start_page"], c["chapter_id"]) for c in chapters]
    boundaries.sort()

    tagged = []
    for p in pages:
        ch_id = boundaries[0][1]
        for start, cid in boundaries:
            if p["page"] >= start:
                ch_id = cid
        p["chapter_id"] = ch_id
        tagged.append(p)
    return tagged


def chunk_text(text: str, size: int = config.CHUNK_SIZE,
               overlap: int = config.CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping word-level chunks."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i: i + size])
        if chunk:
            chunks.append(chunk)
        i += size - overlap
    return chunks


def build_chunks(tagged_pages: list[dict]) -> list[dict]:
    """Create chunk records from pages."""
    chunks = []
    for p in tagged_pages:
        for c in chunk_text(p["text"]):
            chunks.append({
                "chunk_id": len(chunks),
                "chapter_id": p["chapter_id"],
                "page": p["page"],
                "text": c
            })
    return chunks


def embed(texts: list[str]) -> np.ndarray:
    return MODEL.encode(texts, show_progress_bar=False,
                        normalize_embeddings=True).astype("float32")


# ── main entry point ──────────────────────────────────────────────────────────

def ingest_pdf(pdf_path: str, book_name: str) -> dict:
    """
    Full pipeline: PDF → chunks → embeddings → FAISS index.
    Saves everything to index_store/<book_name>/.
    Returns summary dict.
    """
    store_dir = os.path.join(config.INDEX_FOLDER, book_name)
    os.makedirs(store_dir, exist_ok=True)

    print(f"[ingest] Extracting text from {pdf_path} ...")
    pages = extract_text_by_page(pdf_path)
    if not pages:
        raise ValueError("No text found in PDF. Is it a scanned image-only PDF?")

    chapters = detect_chapters(pages)
    tagged   = assign_pages_to_chapters(pages, chapters)
    chunks   = build_chunks(tagged)

    print(f"[ingest] {len(pages)} pages · {len(chapters)} chapters · {len(chunks)} chunks")

    # embed
    print("[ingest] Embedding chunks (this may take a minute) ...")
    texts = [c["text"] for c in chunks]
    vectors = embed(texts)

    # build FAISS index (inner-product == cosine on normalized vecs)
    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(vectors)

    # persist
    faiss.write_index(index, os.path.join(store_dir, "index.faiss"))
    with open(os.path.join(store_dir, "chunks.pkl"), "wb") as f:
        pickle.dump(chunks, f)
    with open(os.path.join(store_dir, "chapters.json"), "w") as f:
        json.dump(chapters, f, indent=2)

    return {
        "book_name": book_name,
        "pages": len(pages),
        "chapters": len(chapters),
        "chunks": len(chunks)
    }


def load_index(book_name: str):
    """Load a previously built index. Returns (faiss_index, chunks, chapters)."""
    store_dir = os.path.join(config.INDEX_FOLDER, book_name)
    index  = faiss.read_index(os.path.join(store_dir, "index.faiss"))
    with open(os.path.join(store_dir, "chunks.pkl"), "rb") as f:
        chunks = pickle.load(f)
    with open(os.path.join(store_dir, "chapters.json")) as f:
        chapters = json.load(f)
    return index, chunks, chapters
