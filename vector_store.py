# vector_store.py  (REPLACE your existing file with this)

import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
# Use local sentence-transformers embeddings (no Google ADC needed)
from langchain.embeddings import SentenceTransformerEmbeddings
from config import FAISS_DIR, CHUNK_SIZE, CHUNK_OVERLAP

def get_text_chunks(text: str):
    """Chia văn bản dài thành các đoạn nhỏ"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_text(text)

def save_vector_store(chunks, save_path: str = FAISS_DIR):
    """Tạo FAISS index từ các đoạn text và lưu lại (dùng sentence-transformers)"""
    # SentenceTransformers local model (small & fast)
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_texts(chunks, embedding=embeddings)
    vectorstore.save_local(save_path)
    return save_path

def load_vector_store(index_path: str = FAISS_DIR):
    """Tải lại FAISS đã lưu"""
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
