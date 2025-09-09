# 💬 Chat với Tài Liệu – AI Assistant  

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python">
  <img src="https://img.shields.io/badge/Streamlit-1.38-red?logo=streamlit">
  <img src="https://img.shields.io/badge/Google-Gemini-yellow?logo=google">
  <img src="https://img.shields.io/badge/LangChain-AI-green?logo=chainlink">
  <img src="https://img.shields.io/badge/FAISS-VectorDB-orange">
  <img src="https://img.shields.io/badge/Status-Active-success">
</p>

---

## 📖 Mục lục
- [✨ Giới thiệu](#-giới-thiệu)  
- [🚀 Tính năng nổi bật](#-tính-năng-nổi-bật)  
- [🎯 Ý nghĩa & Ứng dụng](#-ý-nghĩa--ứng-dụng)  
- [🛠️ Công nghệ sử dụng](#-công-nghệ-sử-dụng)  
- [⚡ Cài đặt & Chạy](#-cài-đặt--chạy)  
- [📂 Cấu trúc thư mục](#-cấu-trúc-thư-mục)  
- [📸 Demo giao diện](#-demo-giao-diện)  
- [🔮 Hướng phát triển](#-hướng-phát-triển)  
- [👨‍💻 Tác giả](#-tác-giả)  
- [📜 License](#-license)  

---

## ✨ Giới thiệu
**Chat với Tài Liệu – AI Assistant** là ứng dụng web cho phép bạn **upload tài liệu** (PDF, Word, Excel, Hình ảnh OCR, …) và **trò chuyện trực tiếp với nội dung bên trong**.  
Không cần đọc thủ công hàng trăm trang, chỉ cần hỏi – AI sẽ trả lời dựa trên dữ liệu bạn đã cung cấp.  

👉 [Dùng thử trực tiếp tại đây](https://duancuoikhoa-2r8svfuhpaegzj7dxlbegd.streamlit.app)

---

## 🚀 Tính năng nổi bật
- Upload nhiều loại tài liệu: **PDF, Word, Excel, Hình ảnh**  
- Trích xuất thông tin bằng **FAISS Vector Database**  
- Trò chuyện tự nhiên nhờ **Google Gemini + LangChain**  
- Bot hiển thị file đang đọc khi trả lời  
- Lưu lịch sử chat & tài liệu đã tải  
- Tải câu trả lời về dưới dạng **PDF / DOCX / TXT**  
- UI giống ChatGPT: có hiệu ứng typing, layout full-screen  

---

## 🎯 Ý nghĩa & Ứng dụng
- **Sinh viên**: Tóm tắt giáo trình, slide nhanh chóng  
- **Văn phòng**: Tra cứu nội dung hợp đồng, báo cáo Excel  
- **Luật/Pháp lý**: Tìm nhanh điều khoản trong văn bản  
- **Y tế**: Hỗ trợ đọc hồ sơ bệnh án, báo cáo xét nghiệm  

💡 **AI đọc tài liệu giúp tiết kiệm 80% thời gian**  

---

## 🛠️ Công nghệ sử dụng
- **Streamlit** – Giao diện web thân thiện  
- **LangChain** – Xử lý truy vấn vectơ hiệu quả  
- **Google Gemini API** – Nền tảng AI nội dung  
- **FAISS** – Tìm kiếm nội dung trong file bằng vector  
- **Thư viện Python**:
  - `PyPDF2`, `python-docx`, `openpyxl` → xử lý file  
  - `pillow`, `pytesseract` → OCR ảnh  
  - `reportlab` → Xuất PDF, `python-docx` → Xuất Word  

---

## ⚡ Cài đặt & Chạy

```bash
# Clone repo về máy
git clone https://github.com/vovanminhtri2002/Du_An_Cuoi_Khoa.git
cd Du_An_Cuoi_Khoa

# Cài thư viện cần thiết
pip install -r requirements.txt

# Tạo file .env tại thư mục gốc, thêm dòng:
# GEMINI_API_KEY=your_api_key_here

# Chạy ứng dụng
streamlit run app.py

---

## 📂 Cấu trúc thư mục

```bash
├── app.py              # Ứng dụng chính
├── data_loader.py      # Module xử lý và trích xuất nội dung
├── vector_store.py     # Module tạo & lưu vector bằng FAISS
├── config.py           # Cấu hình API Key và model
├── requirements.txt    # Các thư viện cần cài
├── temp_uploads/       # Thư mục chứa file upload tạm
└── README.md           # Mô tả dự án

