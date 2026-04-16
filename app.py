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

# 2. Header & Professional Navigation
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
        
        # المرحلة 1: الملفات الأصلية (Searchable)
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
                                
        # المرحلة 2: ملفات السكانر (OCR)
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes())).convert('L')
        img = ImageOps.autocontrast(img)
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config='--psm 11')
        
        prof_idx = -1
        for i, text in enumerate(data['text']):
            if "prof" in text.lower().strip():
                prof_idx = i
                break
        
        if prof_idx != -1:
            p_x, p_y = data['left'][prof_idx], data['top'][prof_idx]
            p_bottom = p_y + data['height'][prof_idx]
            candidates = []
            for i in range(len(data['text'])):
                word = data['text'][i].strip()
                if word and i != prof_idx:
                    w_x, w_y = data['left'][i], data['top'][i]
                    if p_bottom <= w_y < p_bottom + 60 and abs(w_x - p_x) < 100:
                        candidates.append((w_y, w_x, word))
            if candidates:
                candidates.sort()
                first_line_y = candidates[0][0]
                final_text = " ".join([c[2] for c in candidates if abs(c[0] - first_line_y) < 20])
                doc.close(); return final_text, "OCR"
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

# 2. Text Replacer (Style-Match + Bold)
elif st.session_state.mode == 'replace':
    st.subheader("Precision Style-Match Replacement (Bold Enabled)")
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
                    dict_text = page.get_text("dict")
                    for block in dict_text["blocks"]:
                        if "lines" in block:
                            for line in block["lines"]:
                                for span in line["spans"]:
                                    if old_t in span["text"]:
                                        # سحب الخصائص الأصلية
                                        font_size = span["size"]
                                        font_color = span["color"]
                                        origin = span["origin"]
                                        
                                        # تحويل اللون لـ RGB
                                        r = ((font_color >> 16) & 0xFF) / 255
                                        g = ((font_color >> 8) & 0xFF) / 255
                                        b = (font_color & 0xFF) / 255
                                        
                                        # مسح النص القديم
                                        page.add_redact_annot(span["bbox"], fill=(1,1,1))
                                        page.apply_redactions()
                                        
                                        # كتابة النص الجديد (Bold + Same Style)
                                        page.insert_text(origin, new_t, 
                                                       fontsize=font_size, 
                                                       color=(r, g, b), 
                                                       fontname="helv",
                                                       render_mode=1) # هنا ميزة الـ Bold
                                        modified = True
                if modified:
                    out = io.BytesIO(); doc.save(out)
                    st.success(f"Perfect Match: {p.name}")
                    st.download_button(f"Download {p.name}", out.getvalue(), f"Updated_{p.name}", key=f"repl_{p.name}")
                doc.close()

# 3. Smart Renamer (With ZIP Logic)
elif st.session_state.mode == 'rename':
    st.subheader("Smart File Renamer (ZIP Batch Mode)")
    r_files = st.file_uploader("Upload Project PDFs", type=['pdf'], accept_multiple_files=True)
    if r_files:
        if st.button("Process & Generate ZIP"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                p_bar = st.progress(0)
                for i, f in enumerate(r_files):
                    file_bytes = f.getvalue()
                    profile_name, method = get_profile_hybrid(file_bytes)
                    
                    if profile_name:
                        clean = re.sub(r'[\\/*?:"<>|]', "", profile_name).strip()
                        new_name = f"{clean}.pdf"
                    else:
                        new_name = f"ERROR_{f.name}"
                    
                    zip_file.writestr(new_name, file_bytes)
                    st.write(f"✔️ {f.name} ➡️ {new_name} ({method})")
                    p_bar.progress((i + 1) / len(r_files))
            
            st.success("✅ Process Finished!")
            st.download_button("📥 Download ZIP Package", zip_buffer.getvalue(), "Renamed_Drawings.zip", "application/zip", use_container_width=True)

st.markdown("<div class='footer'>Developed by Ahmed.Abdelmawgoud | EM.TECH OFFICE ENGINEERING © 2026</div>", unsafe_allow_html=True)
