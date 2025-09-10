import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.embeddings import SentenceTransformerEmbeddings
from config import FAISS_DIR, CHUNK_SIZE, CHUNK_OVERLAP

def get_text_chunks(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_text(text)

def save_vector_store(chunks, save_path: str = None):
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_texts(chunks, embedding=embeddings)

    if save_path is None:
        save_path = FAISS_DIR

    os.makedirs(save_path, exist_ok=True)
    vectorstore.save_local(save_path)
    return save_path

def load_vector_store(load_path: str):
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    if not os.path.exists(load_path):
        raise ValueError(f"Folder FAISS không tồn tại: {load_path}")

    # Cho phép load pickle index
    return FAISS.load_local(
        load_path, 
        embeddings, 
        allow_dangerous_deserialization=True
    )