"""
retrieval.py  –  Context Pruning + chunk retrieval
"""
import numpy as np
from collections import defaultdict
import config
from ingest import embed, load_index


def retrieve(query: str, book_name: str):
    """
    Context Pruning pipeline:
      1. Embed the query.
      2. Score every chapter by the sum of its chunks' similarities → keep TOP_K_CHAPTERS.
      3. Within kept chapters, pick TOP_K_CHUNKS most similar chunks.
    Returns (selected_chunks, pruning_stats).
    """
    index, chunks, chapters = load_index(book_name)

    q_vec = embed([query])   # shape (1, dim)

    # --- Step 1: score ALL chunks ---
    k_search = min(len(chunks), 50)   # cast a wide net first
    sims, ids = index.search(q_vec, k_search)
    sims, ids = sims[0], ids[0]       # flatten

    # --- Step 2: aggregate per chapter (sum of top similarities) ---
    chapter_scores = defaultdict(float)
    chapter_chunk_map = defaultdict(list)   # chapter_id → [(sim, chunk)]

    for sim, idx in zip(sims, ids):
        if idx < 0:
            continue
        chunk = chunks[idx]
        ch_id = chunk["chapter_id"]
        chapter_scores[ch_id] += float(sim)
        chapter_chunk_map[ch_id].append((float(sim), chunk))

    total_chapters = len(set(c["chapter_id"] for c in chunks))
    top_chapters = sorted(chapter_scores, key=chapter_scores.get, reverse=True)[
        : config.TOP_K_CHAPTERS
    ]

    # --- Step 3: pick best chunks from kept chapters ---
    candidate_chunks = []
    for ch_id in top_chapters:
        candidate_chunks.extend(chapter_chunk_map[ch_id])

    candidate_chunks.sort(key=lambda x: x[0], reverse=True)
    selected = [ch for _, ch in candidate_chunks[: config.TOP_K_CHUNKS]]

    stats = {
        "total_chapters": total_chapters,
        "pruned_to_chapters": len(top_chapters),
        "total_chunks": len(chunks),
        "sent_chunks": len(selected),
        "chapter_titles": [
            next((c["title"] for c in chapters if c["chapter_id"] == cid), str(cid))
            for cid in top_chapters
        ]
    }
    return selected, stats
