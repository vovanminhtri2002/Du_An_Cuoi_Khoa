import streamlit as st
import data_loader, vector_store
import google.generativeai as genai
import os
from config import GEMINI_API_KEY, CHAT_MODEL
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# Config
genai.configure(api_key=GEMINI_API_KEY)
st.set_page_config(page_title="Chat với tài liệu", layout="wide")

# Tạo thư mục lưu file tạm
TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

if "history" not in st.session_state:
    st.session_state.history = []
if "files" not in st.session_state:
    st.session_state.files = []
if "file_history" not in st.session_state:
    st.session_state.file_history = []   # chỉ lưu tên file

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("📂 Tài liệu của bạn")
    uploaded_file = st.file_uploader(
        "Tải file (PDF, Word, Excel, Ảnh)",
        type=["pdf", "docx", "xlsx", "png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

    if uploaded_file:
        for file in uploaded_file:
            if file.name not in [f["name"] for f in st.session_state.files]:
                with st.status(f"⏳ Đang xử lý file: {file.name}", expanded=True) as status:
                    # Lưu file vào thư mục riêng
                    temp_path = os.path.join(TEMP_DIR, file.name)
                    with open(temp_path, "wb") as f:
                        f.write(file.read())

                    # Xử lý file
                    text = data_loader.load_file(temp_path)
                    chunks = vector_store.get_text_chunks(text)
                    db_path = vector_store.save_vector_store(chunks)

                    st.session_state.files.append({
                        "name": file.name,
                        "path": temp_path,
                        "text": text,
                        "db": vector_store.load_vector_store(db_path)
                    })

                    # Ghi vào lịch sử
                    if file.name not in st.session_state.file_history:
                        st.session_state.file_history.append(file.name)

                    status.update(label=f"✅ File đã được xử lý: {file.name}", state="complete")

        uploaded_file = None  # reset uploader tránh load lại

    # Hiển thị lịch sử tải file (chỉ tên + nút xóa)
    if st.session_state.file_history:
        st.markdown("### 🕑 Lịch sử tải file:")
        for i, fname in enumerate(st.session_state.file_history):
            col1, col2 = st.columns([4,1])
            with col1:
                st.markdown(f"- {fname}")
            with col2:
                if st.button("❌", key=f"hist_del_{i}"):
                    st.session_state.file_history.pop(i)
                    st.rerun()

# ---------------- Chat Area ----------------
st.title("💬 Chat với tài liệu")

# CSS custom cho chat giống ChatGPT (giữ nguyên)
st.markdown("""
    <style>
    .stChatMessage.user {
        background-color: #d4f1ff !important;
        border-radius: 10px;
        padding: 8px;
    }
    .stChatMessage.assistant {
        background-color: #f1f1f1 !important;
        border-radius: 10px;
        padding: 8px;
    }
    .typing {
        display: inline-block;
        width: 1em;
        height: 1em;
        border-radius: 50%;
        background-color: #999;
        animation: blink 1.4s infinite both;
        margin: 0 2px;
    }
    @keyframes blink {
        0% { opacity: .2; }
        20% { opacity: 1; }
        100% { opacity: .2; }
    }
    </style>
""", unsafe_allow_html=True)

# Hiển thị lịch sử chat hiện có
chat_container = st.container()
with chat_container:
    for msg in st.session_state.history:
        with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])

# Xử lý input người dùng
if query := st.chat_input("Nhập câu hỏi..."):
    # 1) Lưu user message vào history + hiển thị ngay
    st.session_state.history.append({"role": "user", "content": query})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(query)

    # 2) Hiển thị 1 ô assistant duy nhất làm placeholder typing
    with st.chat_message("assistant", avatar="🤖"):
        typing_placeholder = st.empty()
        typing_placeholder.markdown(
            '<span class="typing"></span><span class="typing"></span><span class="typing"></span>',
            unsafe_allow_html=True
        )

        # 3) Chuẩn bị danh sách file đã upload
        file_names = [f["name"] for f in st.session_state.files]
        # Tìm file được nhắc trong query (so sánh cả tên đầy đủ và tên không mở rộng)
        mentioned_files = []
        qlow = query.lower()
        for name in file_names:
            name_low = name.lower()
            name_noext = os.path.splitext(name_low)[0]
            if name_low in qlow or name_noext in qlow:
                mentioned_files.append(name)

        # Nếu có file được nhắc, chỉ dùng những file đó; không thì dùng tất cả
        if mentioned_files:
            target_files = [f for f in st.session_state.files if f["name"] in mentioned_files]
            reading_info = " ,".join(mentioned_files)
            # hiển thị thông tin nhỏ trong main area (cùng block assistant)
            typing_placeholder.markdown(f"📖 Bot đang đọc: **{reading_info}**<br><br>" +
                                       '<span class="typing"></span><span class="typing"></span><span class="typing"></span>',
                                       unsafe_allow_html=True)
        else:
            target_files = st.session_state.files[:]  # copy toàn bộ
            typing_placeholder.markdown("📖 Bot đang đọc: **tất cả file đã tải lên**<br><br>" +
                                       '<span class="typing"></span><span class="typing"></span><span class="typing"></span>',
                                       unsafe_allow_html=True)

        # 4) Lấy context từ các target_files (chỉ khi có db)
        context_parts = []
        for f in target_files:
            db = f.get("db")
            if not db:
                # Nếu file chưa có db (khoảng hợp bạn muốn chỉ lưu lịch sử), bỏ qua
                continue
            try:
                # Chỉ search nếu query thực sự có nội dung
                if query and query.strip():
                    results = db.similarity_search(query, k=2)
                    context_parts.extend([r.page_content for r in results if r and getattr(r, "page_content", None)])
            except Exception as e:
                # Nếu embed/search lỗi, skip file này (không crash app)
                # Bạn có thể log lỗi nếu cần: st.write(f"Search error for {f['name']}: {e}")
                continue

        context = "\n\n".join(context_parts).strip()

        # 5) Nếu không có context (chưa processed file nào), trả lời hướng dẫn
        if not context:
            reply = ("Mình chưa tìm thấy nội dung từ các file đã xử lý. "
                     "Hãy đảm bảo bạn đã upload và file đã được xử lý (tạo index) trước khi hỏi, "
                     "hoặc gõ rõ 'đọc [tên file]' để chỉ định file.")
            typing_placeholder.markdown(reply, unsafe_allow_html=True)
            st.session_state.history.append({"role": "assistant", "content": reply})
        else:
            # 6) Gọi model (bọc try/except để bắt lỗi quota / network)
            prompt = f"Trả lời câu hỏi dựa trên nội dung sau:\n\n{context}\n\nCâu hỏi: {query}"
            try:
                model = genai.GenerativeModel(CHAT_MODEL)
                response = model.generate_content(prompt)
                answer = response.text if hasattr(response, "text") else str(response)
            except Exception as e:
                # Hiển thị lỗi thân thiện (ví dụ quota)
                err_msg = f"❌ Lỗi khi gọi API: {e}"
                typing_placeholder.markdown(err_msg, unsafe_allow_html=True)
                st.session_state.history.append({"role": "assistant", "content": err_msg})
            else:
                # 7) Thay typing bằng câu trả lời thật (ghi vào history)
                typing_placeholder.markdown(answer, unsafe_allow_html=True)
                st.session_state.history.append({"role": "assistant", "content": answer})
                
# ---- Tải về đoạn chat nếu người dùng yêu cầu ----
if query is not None and any(kw in query.lower() for kw in ["tải về", "xuất file", "download"]):
    # xử lý tải về
    # Cho phép chọn định dạng
    export_format = st.radio("Chọn định dạng tải về:", ["PDF", "DOCX", "TXT"], horizontal=True)

    if export_format == "PDF":
        from io import BytesIO
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = [Paragraph(answer, styles["Normal"])]
        doc.build(story)
        buffer.seek(0)
        st.download_button("⬇️ Tải về PDF", data=buffer, file_name="chatbot_output.pdf", mime="application/pdf")

    elif export_format == "DOCX":
        from io import BytesIO
        from docx import Document
        doc = Document()
        doc.add_paragraph(answer)
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        st.download_button("⬇️ Tải về DOCX", data=buffer, file_name="chatbot_output.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    elif export_format == "TXT":
        st.download_button("⬇️ Tải về TXT", data=answer, file_name="chatbot_output.txt", mime="text/plain")
