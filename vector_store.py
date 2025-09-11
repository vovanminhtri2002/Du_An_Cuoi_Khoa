# ---------------- Imports ----------------
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.embeddings import SentenceTransformerEmbeddings
from config import FAISS_DIR, CHUNK_SIZE, CHUNK_OVERLAP

# ---------------- Text Processing ----------------
def get_text_chunks(text: str):
    """
    Chia văn bản thành các chunk nhỏ dựa trên CHUNK_SIZE và CHUNK_OVERLAP.
    Trả về list các chuỗi.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_text(text)

# ---------------- Embeddings ----------------
def get_embeddings():
    """
    Tạo embeddings bằng SentenceTransformer.
    Ép chạy trên CPU để tránh lỗi metadata tensor.
    """
    return SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

# ---------------- Vector Store ----------------
def save_vector_store(chunks, save_path: str = None):
    """
    Lưu các chunks thành FAISS vector store.
    Nếu save_path không cung cấp, lưu vào FAISS_DIR mặc định.
    """
    embeddings = get_embeddings()
    vectorstore = FAISS.from_texts(chunks, embedding=embeddings)

    save_path = save_path or FAISS_DIR
    os.makedirs(save_path, exist_ok=True)
    vectorstore.save_local(save_path)

    return save_path

def load_vector_store(load_path: str):
    """
    Load FAISS vector store từ folder.
    allow_dangerous_deserialization=True để load index pickle.
    """
    if not os.path.exists(load_path):
        raise ValueError(f"Folder FAISS không tồn tại: {load_path}")

    embeddings = get_embeddings()
    return FAISS.load_local(
        load_path,
        embeddings,
        allow_dangerous_deserialization=True
    )