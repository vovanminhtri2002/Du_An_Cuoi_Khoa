import streamlit as st
import os
import data_loader, vector_store
import google.generativeai as genai
from config import GEMINI_API_KEY, CHAT_MODEL
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re
import shutil
from io import BytesIO

# ---------------- Fonts ----------------
pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))

# ---------------- Config ----------------
genai.configure(api_key=GEMINI_API_KEY)
st.set_page_config(page_title="Chat với tài liệu", layout="wide")
TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

# ---------------- Session state ----------------
if "history" not in st.session_state:
    st.session_state.history = []
if "files" not in st.session_state:
    st.session_state.files = {}

# ---------------- Helper delete ----------------
def delete_file(fname):
    file_data = st.session_state.files.get(fname)
    if file_data:
        # Xoá file tạm
        if os.path.exists(file_data["path"]):
            os.remove(file_data["path"])
        # Xoá folder FAISS
        file_base = os.path.splitext(fname)[0]
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', file_base)
        faiss_folder = os.path.join(vector_store.FAISS_DIR, safe_name)
        if os.path.exists(faiss_folder):
            shutil.rmtree(faiss_folder)
        # Xoá khỏi session
        if fname in st.session_state.files:
            del st.session_state.files[fname]
        st.experimental_rerun()

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("📂 Tài liệu của bạn")
    uploaded_files = st.file_uploader(
        "Tải file (PDF, Word, Excel, Ảnh)...",
        type=["pdf", "docx", "xlsx", "png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

    if uploaded_files:
        for file in uploaded_files:
            if file.name in st.session_state.files:
                continue
            # Lưu file tạm
            temp_path = os.path.join(TEMP_DIR, file.name)
            with open(temp_path, "wb") as f:
                f.write(file.read())
            # Đọc nội dung
            text = data_loader.load_file(temp_path)
            chunks = vector_store.get_text_chunks(text)
            # sanitize tên file, bỏ extension và chỉ còn a-z, A-Z, 0-9, _,-
            file_base = os.path.splitext(file.name)[0]
            safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', file_base)
            db_path = os.path.join(vector_store.FAISS_DIR, safe_name)
            os.makedirs(db_path, exist_ok=True)
            # lưu FAISS index
            vector_store.save_vector_store(chunks, save_path=db_path)
            # load FAISS
            db = vector_store.load_vector_store(db_path)
            # lưu vào session
            st.session_state.files[file.name] = {
                "file_obj": file,
                "path": temp_path,
                "text": text,
                "db": db,
                "db_path": db_path
            }

    # Hiển thị file chính thức
    st.subheader("📌 File đang sử dụng:")
    for fname in list(st.session_state.files.keys()):
        col1, col2 = st.columns([4,1])
        col1.write(fname)
        if col2.button("❌", key=f"remove_active_{fname}"):
            delete_file(fname)
            st.experimental_rerun()

    # Lịch sử tải file
    st.subheader("🕑 Lịch sử tải file:")
    for fname in list(st.session_state.files.keys()):
        col1, col2 = st.columns([4,1])
        col1.write(fname)
        if col2.button("❌", key=f"remove_history_{fname}"):
            delete_file(fname)
            st.experimental_rerun()

# ---------------- Chat area ----------------
st.title("💬 Chat với tài liệu")

st.markdown("""
<style>
.stChatMessage.user {background-color: #d4f1ff !important; border-radius: 10px; padding: 8px;}
.stChatMessage.assistant {background-color: #f1f1f1 !important; border-radius: 10px; padding: 8px;}
.typing {display:inline-block; width:1em; height:1em; border-radius:50%; background-color:#999; animation: blink 1.4s infinite both; margin:0 2px;}
@keyframes blink {0% {opacity:.2;} 20% {opacity:1;} 100% {opacity:.2;}}
</style>
""", unsafe_allow_html=True)

chat_container = st.container()
with chat_container:
    for msg in st.session_state.history:
        with st.chat_message(msg["role"], avatar="🧑" if msg["role"]=="user" else "🤖"):
            st.markdown(msg["content"])

# Input
if query := st.chat_input("Nhập câu hỏi..."):
    st.session_state.history.append({"role":"user","content":query})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(query)
    with st.chat_message("assistant", avatar="🤖") as msg:
        typing_placeholder = st.empty()
        typing_placeholder.markdown('<span class="typing"></span>'*3, unsafe_allow_html=True)
        # chọn target files
        file_names = [f for f in st.session_state.files.keys()]
        mentioned_files = []
        qlow = query.lower()
        for name in file_names:
            name_low = name.lower()
            name_noext = os.path.splitext(name_low)[0]
            if name_low in qlow or name_noext in qlow:
                mentioned_files.append(name)
        if mentioned_files:
            target_files = [st.session_state.files[n] for n in mentioned_files]
            reading_info = ", ".join(mentioned_files)
            typing_placeholder.markdown(f"📖 Bot đang đọc: **{reading_info}**<br><br>"+'<span class="typing"></span>'*3, unsafe_allow_html=True)
        else:
            target_files = list(st.session_state.files.values())
            typing_placeholder.markdown("📖 Bot đang đọc: **tất cả file đã tải lên**<br><br>"+'<span class="typing"></span>'*3, unsafe_allow_html=True)
        # Lấy context
        context_parts = []
        for f in target_files:
            db = f.get("db")
            if not db: continue
            try:
                results = db.similarity_search(query, k=2)
                context_parts.extend([r.page_content for r in results if r and getattr(r,"page_content",None)])
            except: continue
        context = "\n\n".join(context_parts).strip()
        if not context:
            reply = "Mình chưa tìm thấy nội dung từ các file đã xử lý. Hãy đảm bảo đã upload và tạo index trước khi hỏi."
            typing_placeholder.markdown(reply, unsafe_allow_html=True)
            st.session_state.history.append({"role":"assistant","content":reply})
            st.session_state.last_answer = reply
        else:
            prompt = f"Trả lời câu hỏi dựa trên nội dung sau:\n\n{context}\n\nCâu hỏi: {query}"
            try:
                model = genai.GenerativeModel(CHAT_MODEL)
                response = model.generate_content(prompt)
                answer = response.text if hasattr(response,"text") else str(response)
            except Exception as e:
                err_msg = f"❌ Lỗi khi gọi API: {e}"
                typing_placeholder.markdown(err_msg, unsafe_allow_html=True)
                st.session_state.history.append({"role":"assistant","content":err_msg})
            else:
                typing_placeholder.markdown(answer, unsafe_allow_html=True)
                st.session_state.history.append({"role":"assistant","content":answer})
                st.session_state.last_answer = answer

# ---------------- Export ----------------
def _clean_text_for_plain(s: str) -> str:
    if s is None: return ""
    s = s.strip()
    s = re.sub(r'^[\u2022\*\-\s]+', '', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'\1', s)
    s = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\1', s)
    s = re.sub(r':\*+', ':', s)
    return s

def _clean_text_for_pdf_html(s: str) -> str:
    if s is None: return ""
    s = s.strip()
    s = re.sub(r'^[\u2022\*\-\s]+', '', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', s)
    s = re.sub(r':\*+', ':', s)
    return s

if "last_answer" in st.session_state and st.session_state.last_answer:
    st.markdown("### 📥 Tải về câu trả lời gần nhất:")
    export_format = st.radio("Chọn định dạng:", ["PDF","DOCX","TXT","Excel (code)"], horizontal=True)

    if export_format == "PDF":
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        style = ParagraphStyle(name="Vietnamese", fontName="DejaVuSans", fontSize=11, leading=15, spaceAfter=8)
        story = []
        raw_lines = st.session_state.last_answer.splitlines()
        bullets = []
        for raw in raw_lines:
            line = raw.strip()
            if not line:
                if bullets:
                    story.append(ListFlowable([ListItem(Paragraph(b,style)) for b in bullets], bulletType="bullet"))
                    bullets=[]
                story.append(Spacer(1,8))
                continue
            if re.match(r'^[\u2022\*\-\s]+', raw) or re.match(r'^\d+\.\s', line):
                bullets.append(_clean_text_for_pdf_html(raw))
                continue
            if bullets:
                story.append(ListFlowable([ListItem(Paragraph(b,style)) for b in bullets], bulletType="bullet"))
                bullets=[]
            story.append(Paragraph(_clean_text_for_pdf_html(line), style))
        if bullets:
            story.append(ListFlowable([ListItem(Paragraph(b,style)) for b in bullets], bulletType="bullet"))
        doc.build(story)
        buffer.seek(0)
        st.download_button("⬇️ Tải về PDF", data=buffer, file_name="chatbot_output.pdf", mime="application/pdf")

    elif export_format == "DOCX":
        from docx import Document
        buffer = BytesIO()
        doc = Document()
        def _add_docx_paragraph_with_md_runs(paragraph_obj, text):
            tokens = re.split(r'(\*\*.*?\*\*|\*.*?\*)', text)
            for tok in tokens:
                if not tok: continue
                if tok.startswith("**") and tok.endswith("**") and len(tok)>=4:
                    run = paragraph_obj.add_run(tok[2:-2]); run.bold=True
                elif tok.startswith("*") and tok.endswith("*") and len(tok)>=2:
                    run = paragraph_obj.add_run(tok[1:-1]); run.italic=True
                else:
                    paragraph_obj.add_run(tok)
        for raw in st.session_state.last_answer.splitlines():
            line = raw.strip()
            if not line:
                doc.add_paragraph(""); continue
            if re.match(r'^[\u2022\*\-\s]+', raw):
                p = doc.add_paragraph(style="List Bullet"); _add_docx_paragraph_with_md_runs(p,_clean_text_for_plain(raw)); continue
            if re.match(r'^\d+\.\s', line):
                p = doc.add_paragraph(style="List Number"); _add_docx_paragraph_with_md_runs(p,_clean_text_for_plain(line)); continue
            p = doc.add_paragraph(); _add_docx_paragraph_with_md_runs(p,_clean_text_for_plain(line))
        doc.save(buffer); buffer.seek(0)
        st.download_button("⬇️ Tải về DOCX", data=buffer, file_name="chatbot_output.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    elif export_format == "TXT":
        cleaned_lines = [_clean_text_for_plain(l) if l.strip() else "" for l in st.session_state.last_answer.splitlines()]
        st.download_button("⬇️ Tải về TXT", data="\n".join(cleaned_lines), file_name="chatbot_output.txt", mime="text/plain")

    elif export_format == "Excel (code)":
        st.markdown("### 💡 Gợi ý code để xuất ra Excel (chạy local)")
        example_code = f'''
import pandas as pd
lines = [line.strip() for line in """{st.session_state.last_answer}""".split("\\n") if line.strip()]
df = pd.DataFrame({{"Nội dung": lines}})
df.to_excel("chatbot_output.xlsx", index=False, sheet_name="Chatbot Output")
print("✅ Đã lưu chatbot_output.xlsx")
        '''
        st.code(example_code, language="python")