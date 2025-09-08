# data_loader.py
import os
import docx2txt
import pandas as pd
import pytesseract
from PIL import Image
from PyPDF2 import PdfReader

# Nếu bạn có cài Tesseract riêng thì chỉnh lại đường dẫn ở đây (nếu cần)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def load_pdf(file_path: str) -> str:
    """Đọc nội dung từ file PDF"""
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        text = f"Lỗi đọc PDF: {e}"
    return text


def load_docx(file_path: str) -> str:
    """Đọc nội dung từ file Word (.docx)"""
    try:
        return docx2txt.process(file_path)
    except Exception as e:
        return f"Lỗi đọc DOCX: {e}"


def load_excel(file_path: str) -> str:
    """Đọc nội dung từ file Excel (.xlsx)"""
    try:
        df = pd.read_excel(file_path)
        return df.to_string()
    except Exception as e:
        return f"Lỗi đọc Excel: {e}"


def load_image(file_path: str) -> str:
    """OCR trích xuất văn bản từ ảnh"""
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image, lang="vie+eng")  # OCR tiếng Việt + Anh
        return text
    except Exception as e:
        return f"Lỗi OCR ảnh: {e}"


def load_file(file_path: str) -> str:
    """Xác định loại file và đọc nội dung phù hợp"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return load_pdf(file_path)
    elif ext == ".docx":
        return load_docx(file_path)
    elif ext in [".xls", ".xlsx"]:
        return load_excel(file_path)
    elif ext in [".png", ".jpg", ".jpeg"]:
        return load_image(file_path)
    else:
        return f"❌ Không hỗ trợ định dạng file: {ext}"