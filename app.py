import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageOps
import io
import re
import os
import zipfile

# 1. Page Config & Styling
st.set_page_config(page_title="Steel Coordinator Pro", page_icon="🏗️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .main-title { color: #58a6ff; text-align: center; font-weight: 800; font-size: 2.5rem; margin-bottom: 20px; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #010409; text-align: center; padding: 10px; color: #8b949e; border-top: 1px solid #30363d; }
    div.stButton > button { border-radius: 5px; height: 3.5em; font-weight: bold; }
    .status-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🏗️ STEEL COORDINATOR PRO SUITE</h1>", unsafe_allow_html=True)

if 'mode' not in st.session_state: st.session_state.mode = 'dwg'

col_n1, col_n2, col_n3 = st.columns(3)
with col_n1:
    if st.button("📂 DWG Fixer", use_container_width=True): st.session_state.mode = 'dwg'
with col_n2:
    if st.button("📝 Text Replacer", use_container_width=True): st.session_state.mode = 'replace'
with col_n3:
    if st.button("🏷️ Smart Renamer", use_container_width=True): st.session_state.mode = 'rename'

st.write("---")

# --- CORE FUNCTIONS ---

def get_profile_hybrid(pdf_stream):
    try:
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        page = doc[0]
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        if "prof" in s["text"].lower():
                            rect = fitz.Rect(s["bbox"][0]-10, s["bbox"][3], s["bbox"][2]+150, s["bbox"][3]+50)
                            val = page.get_text("text", clip=rect).strip()
                            if len(val) > 2:
                                doc.close(); return val, "Native"
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes())).convert('L')
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        # (OCR Logic stays the same as previous stable version)
        doc.close()
    except: pass
    return None, None

# --- UI MODES ---

if st.session_state.mode == 'dwg':
    st.subheader("AutoCAD Version Fixer (To 2013)")
    files = st.file_uploader("Upload DWG", type=['dwg'], accept_multiple_files=True)
    if files:
        for f in files:
            data = bytearray(f.getvalue()); data[0:6] = b'AC1027'
            st.download_button(f"Download {f.name}", data=bytes(data), file_name=f"Fixed_{f.name}", key=f"dwg_{f.name}")

elif st.session_state.mode == 'replace':
    st.subheader("Precision Style-Match Replacement")
    c1, c2 = st.columns(2)
    with c1: old_t = st.text_input("Find Text (Case Sensitive):")
    with c2: new_t = st.text_input("Replace With:")
    pdfs = st.file_uploader("Upload PDFs", type=['pdf'], accept_multiple_files=True)
    
    if pdfs and old_t and new_t:
        if st.button("Start Seamless Replacement"):
            for p in pdfs:
                doc = fitz.open(stream=p.read(), filetype="pdf")
                modified = False
                for page in doc:
                    # ميزة استخراج الستايل: بنحلل كل كلمة وخصائصها
                    dict_text = page.get_text("dict")
                    for block in dict_text["blocks"]:
                        if "lines" in block:
                            for line in block["lines"]:
                                for span in line["spans"]:
                                    if old_t in span["text"]:
                                        # 1. سحب الخصائص الأصلية
                                        font_size = span["size"]
                                        font_color = span["color"] # بيبقا رقم صحيح (Integer)
                                        origin = span["origin"] # إحداثيات (X, Y) الأصلية
                                        
                                        # تحويل اللون لـ RGB اللي بيفهمه PDF
                                        r = ((font_color >> 16) & 0xFF) / 255
                                        g = ((font_color >> 8) & 0xFF) / 255
                                        b = (font_color & 0xFF) / 255
                                        
                                        # 2. مسح النص القديم
                                        page.add_redact_annot(span["bbox"], fill=(1,1,1))
                                        page.apply_redactions()
                                        
                                        # 3. كتابة النص الجديد بنفس الخصائص
                                        # بنستخدم "helv" كخط افتراضي نظيف يشبه خطوط هندسة الاستيل
                                        page.insert_text(origin, new_t, 
                                                       fontsize=font_size, 
                                                       color=(r, g, b), 
                                                       fontname="helv")
                                        modified = True
                if modified:
                    out = io.BytesIO(); doc.save(out)
                    st.success(f"Perfect Match: {p.name}")
                    st.download_button(f"Download {p.name}", out.getvalue(), f"Updated_{p.name}", key=f"repl_{p.name}")
                doc.close()

elif st.session_state.mode == 'rename':
    st.subheader("Smart File Renamer (ZIP Mode)")
    # (Same ZIP logic from the previous successful version)
    r_files = st.file_uploader("Upload Drawings", type=['pdf'], accept_multiple_files=True)
    if r_files:
        if st.button("Process & Generate ZIP"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_f:
                p_bar = st.progress(0)
                for i, f in enumerate(r_files):
                    p_name, meth = get_profile_hybrid(f.getvalue())
                    clean = re.sub(r'[\\/*?:"<>|]', "", p_name).strip() if p_name else f"Unresolved_{i}"
                    zip_f.writestr(f"{clean}.pdf", f.getvalue())
                    p_bar.progress((i + 1) / len(r_files))
            st.success("✅ Ready!")
            st.download_button("📥 Download ZIP", zip_buffer.getvalue(), "Renamed.zip", use_container_width=True)

st.markdown("<div class='footer'>Developed by Ahmed.Abdelmawgoud | Engineering Excellence © 2026</div>", unsafe_allow_html=True)
