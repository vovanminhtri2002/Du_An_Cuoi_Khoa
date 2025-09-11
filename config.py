# ---------------- Imports ----------------
import os
from dotenv import load_dotenv
import google.generativeai as genai

# ---------------- Load Environment ----------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("❌ Không tìm thấy GEMINI_API_KEY trong file .env")

# ---------------- Configure Gemini ----------------
genai.configure(api_key=GEMINI_API_KEY)

# ---------------- Model Settings ----------------
CHAT_MODEL = "models/gemini-1.5-flash"       # QA chain
VISION_MODEL = "models/gemini-1.5-flash"
EMBEDDING_MODEL = "models/embedding-001"

# ---------------- Text Processing ----------------
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 200

# ---------------- Storage ----------------
FAISS_DIR = "faiss_index"