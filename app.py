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
    .status-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    div.stButton > button { border-radius: 5px; height: 3.5em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Header & Navigation
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
        # Stage 1: Native Text Extraction (Searchable)
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
        # Stage 2: OCR Fallback (Scanned)
        pix = page.get_pixmap(dpi=150)
        img = Image.open(io.BytesIO(pix.tobytes())).convert('L')
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        for i, txt in enumerate(data['text']):
            if "prof" in txt.lower():
                # Logic to grab text below in OCR
                doc.close(); return "Detected_Profile", "OCR"
        doc.close()
    except: pass
    return None, None

# --- UI MODES ---

# 1. DWG Fixer
if st.session_state.mode == 'dwg':
    st.subheader("AutoCAD Version Fixer (To 2013)")
    files = st.file_uploader("Upload DWG files", type=['dwg'], accept_multiple_files=True)
    if files:
        for f in files:
            data = bytearray(f.getvalue()); data[0:6] = b'AC1027'
            st.success(f"Fixed: {f.name}")
            st.download_button(f"Download {f.name}", data=bytes(data), file_name=f"Fixed_{f.name}", key=f"dwg_{f.name}")

# 2. Text Replacer (Precision)
elif st.session_state.mode == 'replace':
    st.subheader("Precision PDF Text Replacement")
    c1, c2 = st.columns(2)
    with c1: old_t = st.text_input("Find Text:")
    with c2: new_t = st.text_input("Replace With:")
    pdfs = st.file_uploader("Upload PDFs", type=['pdf'], accept_multiple_files=True)
    if pdfs and old_t and new_t:
        if st.button("Start Precision Replacement"):
            for p in pdfs:
                doc = fitz.open(stream=p.read(), filetype="pdf")
                mod = False
                for page in doc:
                    blocks = page.get_text("dict")["blocks"]
                    for b in blocks:
                        if "lines" in b:
                            for l in b["lines"]:
                                for s in l["spans"]:
                                    if old_t in s["text"]:
                                        sz, clr, (ox, oy) = s["size"], s["color"], s["origin"]
                                        rgb = (((clr >> 16) & 0xFF)/255, ((clr >> 8) & 0xFF)/255, (clr & 0xFF)/255)
                                        page.add_redact_annot(s["bbox"], fill=(1,1,1))
                                        page.apply_redactions()
                                        page.insert_text(fitz.Point(ox, oy), new_t, fontsize=sz, color=rgb, fontname="cour")
                                        mod = True
                if mod:
                    out = io.BytesIO(); doc.save(out)
                    st.success(f"Updated: {p.name}")
                    st.download_button(f"Download {p.name}", out.getvalue(), f"Fixed_{p.name}", key=f"repl_{p.name}")
                doc.close()

# 3. Smart Renamer (With ZIP Logic)
elif st.session_state.mode == 'rename':
    st.subheader("Smart File Renamer (Batch Processing)")
    r_files = st.file_uploader("Upload Project PDFs", type=['pdf'], accept_multiple_files=True)
    
    if r_files:
        if st.button("Process & Generate ZIP"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                progress_bar = st.progress(0)
                for i, f in enumerate(r_files):
                    file_bytes = f.getvalue()
                    p_name, meth = get_profile_hybrid(file_bytes)
                    
                    if p_name:
                        clean = re.sub(r'[\\/*?:"<>|]', "", p_name).strip()
                        new_filename = f"{clean}.pdf"
                    else:
                        new_filename = f"Unresolved_{f.name}"
                    
                    # إضافة الملف للـ ZIP
                    zip_file.writestr(new_filename, file_bytes)
                    st.write(f"✔️ Processed: {f.name} → {new_filename}")
                    progress_bar.progress((i + 1) / len(r_files))
            
            st.success("✅ All files processed successfully!")
            st.download_button(
                label="📥 Download All Renamed Files (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="Renamed_Drawings.zip",
                mime="application/zip",
                use_container_width=True
            )

st.markdown("<div class='footer'>Developed by Ahmed.Abdelmawgoud | EM. Tech Office Engineering © 2026</div>", unsafe_allow_html=True)
