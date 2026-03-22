"""
generation.py  –  Call Gemini Flash with pruned context
"""
import google.generativeai as genai
import config

genai.configure(api_key=config.GEMINI_API_KEY)
model = genai.GenerativeModel(config.GEMINI_MODEL)


def build_prompt(query: str, chunks: list[dict]) -> str:
    context = "\n\n---\n\n".join(
        f"[Page {c['page']}]\n{c['text']}" for c in chunks
    )
    return (
        "You are a tutor for state-board students in India.\n\n"
        "Rules:\n"
        "1. Answer ONLY from the context provided below.\n"
        "2. Give a COMPLETE answer — never stop mid-sentence.\n"
        "3. Keep it concise: 4 to 6 sentences maximum.\n"
        "4. Use simple, clear language a school student can understand.\n"
        "5. If the answer is not in the context, say exactly: "
        "'I could not find that in the textbook.'\n\n"
        f"TEXTBOOK CONTEXT:\n{context}\n\n"
        f"STUDENT QUESTION: {query}\n\n"
        "ANSWER (complete, 4-6 sentences):"
    )


def generate_answer(query: str, chunks: list[dict]) -> dict:
    """Returns {answer, prompt_tokens, completion_tokens, cost_usd}."""
    prompt = build_prompt(query, chunks)

    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            max_output_tokens=config.MAX_TOKENS_RESPONSE,
            temperature=0.3,
        )
    )

    answer = response.text.strip()

    # Token counts (Gemini returns them in usage_metadata)
    usage = response.usage_metadata
    prompt_tokens     = getattr(usage, "prompt_token_count", 0) or 0
    completion_tokens = getattr(usage, "candidates_token_count", 0) or 0

    # Gemini 2.0 Flash pricing (as of early 2025):
    # Input:  $0.075 / 1M tokens
    # Output: $0.30  / 1M tokens
    cost = (prompt_tokens / 1_000_000 * 0.075) + \
           (completion_tokens / 1_000_000 * 0.30)

    return {
        "answer":           answer,
        "prompt_tokens":    prompt_tokens,
        "completion_tokens":completion_tokens,
        "cost_usd":         round(cost, 6)
    }
