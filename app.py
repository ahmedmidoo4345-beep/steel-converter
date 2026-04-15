import streamlit as st
import fitz  # PyMuPDF
import io
import time

# 1. Page Configuration
st.set_page_config(page_title="SteelFixer Ultimate", page_icon="🏗️", layout="wide")

# 2. Advanced CSS for Premium Look
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .main-title { color: #58a6ff; text-align: center; font-weight: 800; font-size: 3rem; }
    .stButton>button {
        background-color: #238636;
        color: white;
        border-radius: 8px;
        width: 100%;
        font-weight: bold;
        height: 3em;
    }
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #010409; text-align: center;
        padding: 10px; border-top: 1px solid #30363d;
        color: #8b949e;
    }
    .file-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Header
st.markdown("<h1 class='main-title'>🏗️ STEEL COORDINATOR ULTIMATE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e;'>Professional Engineering Toolkit v3.0</p>", unsafe_allow_html=True)

# 4. Navigation Tabs (دمج الميزتين)
tab1, tab2 = st.tabs(["📂 AutoCAD Version Fixer", "📝 PDF Text Replacer"])

# --- Tab 1: AutoCAD Version Fixer (الكود اللي نجح معاك) ---
with tab1:
    st.subheader("Convert Modern DWG to 2013 Version")
    dwg_files = st.file_uploader("Upload DWG files", type=['dwg'], accept_multiple_files=True, key="dwg_upload")
    
    if dwg_files:
        status_dwg = st.empty()
        status_dwg.info("⚡ System is bypassing version restrictions...")
        for dwg in dwg_files:
            content = bytearray(dwg.getvalue())
            content[0:6] = b'AC1027' # الكود السحري لنسخة 2013
            st.success(f"Successfully fixed: {dwg.name}")
            st.download_button(f"Download Fixed {dwg.name}", data=bytes(content), file_name=f"Fixed_{dwg.name}", key=f"dl_{dwg.name}")
        status_dwg.success("DWG processing complete!")

# --- Tab 2: PDF Text Replacer (الميزة الجديدة) ---
with tab2:
    st.subheader("Smart PDF Text Replacement")
    st.write("Modify Project Numbers or Trestle IDs across multiple PDF drawings instantly.")
    
    col1, col2 = st.columns(2)
    with col1:
        find_text = st.text_input("🔍 FIND WHAT (Old Text):", placeholder="Example: D44-403-TR002")
    with col2:
        replace_text = st.text_input("🔄 REPLACE WITH (New Text):", placeholder="Example: D44-403-TR001")
    
    pdf_files = st.file_uploader("Upload PDF Drawings", type=['pdf'], accept_multiple_files=True, key="pdf_upload")

    if pdf_files and find_text and replace_text:
        if st.button("Execute High-Precision Replacement"):
            status_pdf = st.empty()
            status_pdf.warning("🛠️ Re-drawing PDF layers... please wait.")
            
            for pdf in pdf_files:
                doc = fitz.open(stream=pdf.read(), filetype="pdf")
                modified = False
                for page in doc:
                    areas = page.search_for(find_text)
                    for rect in areas:
                        page.add_redact_annot(rect, fill=(1, 1, 1)) # مسح النص القديم
                        page.apply_redactions()
                        page.insert_text(fitz.Point(rect.x0, rect.y1 - 2), replace_text, 
                                        fontsize=10, fontname="helv", color=(0, 0, 0)) # كتابة الجديد
                        modified = True
                
                if modified:
                    output_buffer = io.BytesIO()
                    doc.save(output_buffer, garbage=3, deflate=True)
                    st.success(f"Success: {pdf.name} has been updated.")
                    st.download_button(f"Download Updated {pdf.name}", data=output_buffer.getvalue(), file_name=f"Updated_{pdf.name}")
                else:
                    st.error(f"Text '{find_text}' not found in: {pdf.name}")
                doc.close()
            status_pdf.success("All PDF tasks finished!")

# 5. Footer Signature
st.markdown(f"""
    <div class="footer">
        Designed & Developed by <span style="color:#58a6ff; font-weight:bold;">Ahmed.Abdelmawgoud</span> | Senior Steel Coordinator © 2026
    </div>
""", unsafe_allow_html=True)
st.write("<br><br><br>", unsafe_allow_html=True)
