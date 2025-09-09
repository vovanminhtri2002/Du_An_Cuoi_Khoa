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
- [🛠️ Công nghệ sử dụng](#️-công-nghệ-sử-dụng)
- [⚡ Cài đặt & Chạy](#-cài-đặt--chạy)
- [📂 Cấu trúc thư mục](#-cấu-trúc-thư-mục)
- [📸 Demo giao diện](#-demo-giao-diện)
- [🔮 Hướng phát triển](#-hướng-phát-triển)
- [👨‍💻 Tác giả](#-tác-giả)
- [📜 License](#-license)

---

## ✨ Giới thiệu
**Chat với Tài Liệu – AI Assistant** là ứng dụng web cho phép bạn **upload tài liệu** (PDF, Word, Excel, Hình ảnh OCR, …) và **trò chuyện trực tiếp với nội dung bên trong**.  
Không cần đọc thủ công hàng trăm trang, chỉ cần hỏi – AI sẽ trả lời dựa trên dữ liệu bạn cung cấp.  

---

## 🚀 Tính năng nổi bật
✅ Upload nhiều loại tài liệu: **PDF, Word, Excel, Hình ảnh**  
✅ Trích xuất thông tin bằng **FAISS Vector Database**  
✅ Trò chuyện tự nhiên nhờ **Google Gemini + LangChain**  
✅ Bot hiển thị **đang đọc file nào** khi trả lời  
✅ Lưu **lịch sử chat & file đã tải lên**  
✅ Xuất câu trả lời thành **PDF / DOCX / TXT**  
✅ UI giống ChatGPT: hiệu ứng typing, layout full-screen  

---

## 🎯 Ý nghĩa & Ứng dụng
📚 Sinh viên: tóm tắt tài liệu học tập, đọc nhanh slide/giáo trình.  
🏢 Văn phòng: tìm thông tin trong hợp đồng, báo cáo, dữ liệu Excel.  
⚖️ Luật/Pháp lý: tra cứu điều khoản từ văn bản pháp luật.  
🧑‍⚕️ Y tế: hỗ trợ đọc hồ sơ bệnh án, báo cáo xét nghiệm.  
💡 Nói ngắn gọn: **AI đọc tài liệu hộ bạn – tiết kiệm 80% thời gian**.  

---

## 🛠️ Công nghệ sử dụng
- **Streamlit** → Xây dựng giao diện web  
- **LangChain** → Quản lý truy vấn & pipeline AI  
- **Google Gemini API** → Mô hình ngôn ngữ thông minh  
- **FAISS** → Lưu trữ & tìm kiếm vector hóa dữ liệu  
- **Python Libraries**:  
  - `PyPDF2`, `python-docx`, `openpyxl` → xử lý file  
  - `pillow`, `pytesseract` → OCR hình ảnh  
  - `reportlab`, `python-docx` → Xuất file PDF/DOCX  

---

## ⚡ Cài đặt & Chạy

### 1. Clone repo
```bash
git clone https://github.com/<username>/<repo-name>.git
cd <repo-name>
