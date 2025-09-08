# config.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load biến môi trường từ .env
load_dotenv()

# Lấy API key (ưu tiên GEMINI_API_KEY)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("❌ Không tìm thấy GEMINI_API_KEY trong file .env")

# Cấu hình Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Định nghĩa model mặc định (sau sẽ dùng ở QA chain)
CHAT_MODEL = "models/gemini-1.5-flash"#gemini-1.0-pro#gemini-2.5-pro#gemini-1.5-flash
VISION_MODEL = "models/gemini-1.5-flash"
EMBEDDING_MODEL = "models/embedding-001"

# Tham số chunk (dùng khi xử lý văn bản dài)
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 200

# Thư mục lưu FAISS
FAISS_DIR = "faiss_index"