import os
from dotenv import load_dotenv

load_dotenv()

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL   = "gemini-2.5-flash"        # confirmed available on your key
MAX_TOKENS_RESPONSE = 2048                 # increased for full detailed answers

# Chunking
CHUNK_SIZE    = 400   # words per chunk
CHUNK_OVERLAP = 50    # words overlap between chunks

# Retrieval / Pruning
TOP_K_CHAPTERS = 3    # how many top chapters to keep (context pruning)
TOP_K_CHUNKS   = 8    # how many chunks to send to LLM (more = richer answers)

# Paths
UPLOAD_FOLDER = "uploads"
INDEX_FOLDER  = "index_store"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(INDEX_FOLDER,  exist_ok=True)
