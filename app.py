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

# إدارة حالة المسح (Clear State)
if 'rename_uploader_key' not in st.session_state:
    st.session_state.rename_uploader_key = 0

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
        # Native Stage
        dict_txt = page.get_text("dict")
        for b in dict_txt["blocks"]:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        if "prof" in s["text"].lower():
                            rect = fitz.Rect(s["bbox"][0]-10, s["bbox"][3], s["bbox"][2]+150, s["bbox"][3]+50)
                            val = page.get_text("text", clip=rect).strip()
                            if len(val) > 2:
                                doc.close(); return val, "Native"
        # OCR Stage
        pix = page.get_pixmap(dpi=150)
        img = Image.open(io.BytesIO(pix.tobytes())).convert('L')
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config='--psm 11')
        prof_idx = -1
        for i, text in enumerate(data['text']):
            if "prof" in text.lower().strip():
                prof_idx = i; break
        if prof_idx != -1:
            p_x, p_y = data['left'][prof_idx], data['top'][prof_idx]
            p_bottom = p_y + data['height'][prof_idx]
            cands = []
            for i in range(len(data['text'])):
                word = data['text'][i].strip()
                if word and i != prof_idx:
                    if p_bottom <= data['top'][i] < p_bottom + 60 and abs(data['left'][i] - p_x) < 100:
                        cands.append((data['top'][i], data['left'][i], word))
            if cands:
                cands.sort()
                final = " ".join([c[2] for c in cands if abs(c[0] - cands[0][0]) < 20])
                doc.close(); return final, "OCR"
        doc.close()
    except: pass
    return None, None

# --- UI MODES ---

if st.session_state.mode == 'dwg':
    st.subheader("AutoCAD Version Fixer (To 2013)")
    files = st.file_uploader("Upload DWG files", type=['dwg'], accept_multiple_files=True)
    if files:
        for f in files:
            data = bytearray(f.getvalue()); data[0:6] = b'AC1027'
            st.download_button(f"📥 Download {f.name}", data=bytes(data), file_name=f"Fixed_{f.name}", key=f"dwg_{f.name}")

elif st.session_state.mode == 'replace':
    st.subheader("Precision Style-Match Replacement")
    c1, c2 = st.columns(2)
    with c1: old_t = st.text_input("Find Text (Case Sensitive):")
    with c2: new_t = st.text_input("Replace With:")
    pdfs = st.file_uploader("Upload PDFs", type=['pdf'], accept_multiple_files=True, key="repl_upload")
    if pdfs and old_t and new_t:
        if st.button("🚀 Start Seamless Replacement", use_container_width=True):
            for p in pdfs:
                doc = fitz.open(stream=p.read(), filetype="pdf")
                mod = False
                for page in doc:
                    dict_t = page.get_text("dict")
                    for b in dict_t["blocks"]:
                        if "lines" in b:
                            for l in b["lines"]:
                                for s in l["spans"]:
                                    if old_t in s["text"]:
                                        sz, clr, ori = s["size"], s["color"], s["origin"]
                                        r, g, b_val = ((clr >> 16) & 0xFF)/255, ((clr >> 8) & 0xFF)/255, (clr & 0xFF)/255
                                        page.add_redact_annot(s["bbox"], fill=(1,1,1))
                                        page.apply_redactions()
                                        page.insert_text(ori, new_t, fontsize=sz, color=(r,g,b_val), fontname="helv", render_mode=1)
                                        mod = True
                if mod:
                    out = io.BytesIO(); doc.save(out)
                    st.success(f"✅ Modified: {p.name}")
                    st.download_button(f"📥 Download {p.name}", out.getvalue(), f"Fixed_{p.name}", key=f"repl_{p.name}_{os.urandom(2).hex()}")
                doc.close()

elif st.session_state.mode == 'rename':
    st.subheader("Smart File Renamer (ZIP Output)")
    
    # صف للأزرار الخاصة بالتحكم
    col_up, col_clr = st.columns([4, 1])
    with col_clr:
        if st.button("🗑️ Clear All Files", use_container_width=True):
            st.session_state.rename_uploader_key += 1
            st.rerun()

    r_files = st.file_uploader("Upload PDFs", type=['pdf'], accept_multiple_files=True, key=f"rename_uploader_{st.session_state.rename_uploader_key}")
    
    if r_files:
        if st.button("📦 Process & Generate ZIP", use_container_width=True):
            zip_buffer = io.BytesIO()
            used_names = {} # قاموس لتتبع الأسماء المتكررة
            
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_f:
                p_bar = st.progress(0)
                for i, f in enumerate(r_files):
                    f_bytes = f.getvalue()
                    p_name, meth = get_profile_hybrid(f_bytes)
                    
                    if p_name:
                        base_name = re.sub(r'[\\/*?:"<>|]', "", p_name).strip()
                        # منطق منع التكرار
                        if base_name in used_names:
                            used_names[base_name] += 1
                            final_name = f"{base_name}_{used_names[base_name]}"
                        else:
                            used_names[base_name] = 0
                            final_name = base_name
                    else:
                        final_name = f"Unresolved_{i}"
                    
                    zip_f.writestr(f"{final_name}.pdf", f_bytes)
                    st.write(f"✔️ {f.name} ➡️ {final_name}.pdf")
                    p_bar.progress((i + 1) / len(r_files))
            
            st.success("✅ Process Finished!")
            st.download_button("📥 Download ZIP Package", zip_buffer.getvalue(), "Renamed_Steel_Drawings.zip", use_container_width=True)

st.markdown("<div class='footer'>Developed by Ahmed.Abdelmawgoud | Engineering Intelligence © 2026</div>", unsafe_allow_html=True)
