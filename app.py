import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageOps
import io
import re
import os

# 1. Page Configuration
st.set_page_config(page_title="Steel Coordinator Ultimate", page_icon="🏗️", layout="wide")

# 2. Premium Styling (Refined for v7.0)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .main-title { color: #58a6ff; text-align: center; font-weight: 800; font-size: 2.8rem; margin-bottom: 0; }
    .stButton>button {
        background-color: #238636; color: white; border-radius: 8px; font-weight: bold; height: 3.5em; width: 100%;
    }
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%; background-color: #010409;
        text-align: center; padding: 12px; color: #8b949e; border-top: 1px solid #30363d;
    }
    .status-card {
        background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Header
st.markdown("<h1 class='main-title'>🏗️ STEEL COORDINATOR ULTIMATE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e;'>All-in-One Professional Engineering Suite v7.0</p>", unsafe_allow_html=True)

# 4. Navigation (Buttons in Header)
col_nav1, col_nav2, col_nav3 = st.columns(3)
with col_nav1:
    dwg_btn = st.button("📂 DWG Version Fixer")
with col_nav2:
    pdf_rep_btn = st.button("📝 PDF Text Replacer")
with col_nav3:
    renamer_btn = st.button("🏷️ Smart File Renamer")

if 'app_mode' not in st.session_state: st.session_state.app_mode = 'dwg'
if dwg_btn: st.session_state.app_mode = 'dwg'
if pdf_rep_btn: st.session_state.app_mode = 'pdf_replacer'
if renamer_btn: st.session_state.app_mode = 'renamer'

st.write("---")

# --- FUNCTIONS ---

def get_profile_hybrid(pdf_stream):
    """Hybrid Logic: Tries Native first, then OCR if needed."""
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    page = doc[0]
    
    # Stage 1: Native Text Extraction
    blocks = page.get_text("dict")["blocks"]
    for b in blocks:
        if "lines" in b:
            for l in b["lines"]:
                for s in l["spans"]:
                    if "prof" in s["text"].lower():
                        search_area = fitz.Rect(s["bbox"][0]-5, s["bbox"][3], s["bbox"][2]+100, s["bbox"][3]+40)
                        val = page.get_text("text", clip=search_area).strip()
                        if len(val) > 2:
                            doc.close()
                            return val, "Native"
    
    # Stage 2: OCR Fallback (If Native fails or yields nothing)
    try:
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes())).convert('L')
        img = ImageOps.autocontrast(img)
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config='--psm 11')
        
        prof_idx = -1
        for i, text in enumerate(data['text']):
            if "prof" in text.lower():
                prof_idx = i
                break
        
        if prof_idx != -1:
            p_bottom = data['top'][prof_idx] + data['height'][prof_idx]
            p_x = data['left'][prof_idx]
            parts = []
            for i in range(len(data['text'])):
                if data['text'][i].strip() and i != prof_idx:
                    if p_bottom <= data['top'][i] < p_bottom + 50 and abs(data['left'][i] - p_x) < 80:
                        parts.append(data['text'][i])
            if parts:
                doc.close()
                return " ".join(parts), "OCR"
    except: pass
    
    doc.close()
    return None, None

# --- MAIN UI LOGIC ---

# 1. DWG Fixer
if st.session_state.app_mode == 'dwg':
    st.subheader("AutoCAD Version Recovery")
    dwg_files = st.file_uploader("Upload DWG files to convert to 2013", type=['dwg'], accept_multiple_files=True)
    if dwg_files:
        for dwg in dwg_files:
            content = bytearray(dwg.getvalue())
            content[0:6] = b'AC1027'
            st.success(f"Fixed: {dwg.name}")
            st.download_button(f"Download {dwg.name}", data=bytes(content), file_name=f"Fixed_{dwg.name}")

# 2. PDF Replacer
elif st.session_state.app_mode == 'pdf_replacer':
    st.subheader("High-Precision PDF Text Replacement")
    col1, col2 = st.columns(2)
    with col1: f_txt = st.text_input("FIND WHAT:")
    with col2: r_txt = st.text_input("REPLACE WITH:")
    p_files = st.file_uploader("Upload PDF Drawings", type=['pdf'], accept_multiple_files=True)
    
    if p_files and f_txt and r_txt:
        if st.button("Run Master Replacement"):
            for p in p_files:
                doc = fitz.open(stream=p.read(), filetype="pdf")
                modified = False
                for page in doc:
                    instances = page.search_for(f_txt)
                    for rect in instances:
                        page.add_redact_annot(rect, fill=(1, 1, 1))
                        page.apply_redactions()
                        page.insert_text(fitz.Point(rect.x0, rect.y1-2), r_txt, fontsize=9, fontname="helv")
                        modified = True
                if modified:
                    out = io.BytesIO(); doc.save(out, garbage=3, deflate=True)
                    st.success(f"Updated: {p.name}")
                    st.download_button(f"Download {p.name}", data=out.getvalue(), file_name=f"Fixed_{p.name}")
                doc.close()

# 3. Smart Renamer (The Hybrid Feature)
elif st.session_state.app_mode == 'renamer':
    st.subheader("Hybrid Smart Renamer (Native + OCR)")
    st.info("System automatically detects if the PDF is Scanned or Searchable.")
    r_files = st.file_uploader("Upload Project PDFs (Batch Mode)", type=['pdf'], accept_multiple_files=True)
    
    if r_files:
        if st.button("Analyze & Rename Files"):
            for r_file in r_files:
                file_stream = r_file.getvalue()
                profile_name, method = get_profile_hybrid(file_stream)
                
                if profile_name:
                    clean_name = re.sub(r'[\\/*?:"<>|]', "", profile_name).strip()
                    st.markdown(f"""
                        <div class="status-card">
                            <b>Original:</b> {r_file.name}<br>
                            <b>Detected Profile:</b> <span style="color:#58a6ff">{clean_name}</span> 
                            <small>(Method: {method})</small>
                        </div>
                    """, unsafe_allow_html=True)
                    st.download_button(f"Download as {clean_name}.pdf", data=file_stream, file_name=f"{clean_name}.pdf")
                else:
                    st.error(f"Could not extract profile from: {r_file.name}")

# 5. Footer
st.markdown(f"""
    <div class="footer">
        Designed by <span style="color:#58a6ff; font-weight:bold;">Ahmed.Abdelmawgoud</span> | Senior Steel Coordinator © 2026
    </div>
""", unsafe_allow_html=True)
