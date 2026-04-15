import streamlit as st
import fitz  # PyMuPDF
import io
import time

# 1. Page Configuration
st.set_page_config(page_title="SteelFixer Executive", page_icon="🏗️", layout="wide")

# 2. Ultra-Premium Styling (Custom Header Nav & Look)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    
    /* Navigation Style */
    .nav-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        padding: 20px;
        background-color: #161b22;
        border-bottom: 2px solid #58a6ff;
        margin-bottom: 30px;
    }
    
    .main-title { color: #58a6ff; text-align: center; font-weight: 800; font-size: 2.5rem; margin-bottom: 5px;}
    
    .file-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-top: 10px;
        transition: 0.3s;
    }
    .file-card:hover { border-color: #58a6ff; }
    
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #010409; text-align: center;
        padding: 10px; border-top: 1px solid #30363d;
        color: #8b949e;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Header & Navigation Logic
st.markdown("<h1 class='main-title'>🏗️ STEEL COORDINATOR EXECUTIVE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e;'>Precision Engineering Hub</p>", unsafe_allow_html=True)

# Navigation Menu using Streamlit Columns for Header Look
col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    dwg_mode = st.button("📂 AutoCAD Version Fixer", use_container_width=True)
with col_nav2:
    pdf_mode = st.button("📝 PDF Smart Replacer", use_container_width=True)

# Initialize Session State for Navigation
if 'mode' not in st.session_state:
    st.session_state.mode = 'dwg'
if dwg_mode: st.session_state.mode = 'dwg'
if pdf_mode: st.session_state.mode = 'pdf'

st.write("---")

# --- MODE 1: AutoCAD FIXER ---
if st.session_state.mode == 'dwg':
    st.subheader("AutoCAD Version Recovery")
    dwg_files = st.file_uploader("Upload DWG files", type=['dwg'], accept_multiple_files=True)
    
    if dwg_files:
        placeholder = st.empty()
        placeholder.info("⚡ Injecting AC1027 (2013) headers...")
        for dwg in dwg_files:
            content = bytearray(dwg.getvalue())
            content[0:6] = b'AC1027'
            st.success(f"Fixed: {dwg.name}")
            st.download_button(f"Download {dwg.name}", data=bytes(content), file_name=f"Fixed_{dwg.name}")

# --- MODE 2: PDF REPLACER (With Style Matching) ---
else:
    st.subheader("High-Precision PDF Text Replacement")
    st.info("System will auto-match font size and color of the original text.")
    
    c1, c2 = st.columns(2)
    with c1:
        find_txt = st.text_input("FIND WHAT:", placeholder="Old text...")
    with c2:
        replace_txt = st.text_input("REPLACE WITH:", placeholder="New text...")
        
    pdf_files = st.file_uploader("Upload PDF Drawings", type=['pdf'], accept_multiple_files=True)

    if pdf_files and find_txt and replace_txt:
        if st.button("Execute Precision Replacement"):
            for pdf in pdf_files:
                doc = fitz.open(stream=pdf.read(), filetype="pdf")
                modified = False
                
                for page in doc:
                    # Search for text with detailed info (to get style)
                    text_instances = page.search_for(find_txt)
                    
                    for rect in text_instances:
                        # Extract original font details
                        dict_info = page.get_text("dict", clip=rect)
                        try:
                            # Get the font properties of the first span found in the area
                            span = dict_info["blocks"][0]["lines"][0]["spans"][0]
                            orig_size = span["size"]
                            orig_color = span["color"] # returns integer color
                            # Convert integer color to RGB tuple
                            r = (orig_color >> 16) & 0xFF
                            g = (orig_color >> 8) & 0xFF
                            b = orig_color & 0xFF
                            rgb_color = (r/255, g/255, b/255)
                        except:
                            orig_size = 10
                            rgb_color = (0, 0, 0)

                        # Apply redaction (clean the area)
                        page.add_redact_annot(rect, fill=(1, 1, 1))
                        page.apply_redactions()
                        
                        # Insert new text with original properties
                        page.insert_text(fitz.Point(rect.x0, rect.y1 - 2), replace_txt, 
                                        fontsize=orig_size, 
                                        color=rgb_color,
                                        fontname="helv")
                        modified = True
                
                if modified:
                    out = io.BytesIO()
                    doc.save(out, garbage=3, deflate=True)
                    st.success(f"Success: {pdf.name}")
                    st.download_button(f"Download {pdf.name}", data=out.getvalue(), file_name=f"Updated_{pdf.name}")
                else:
                    st.error(f"Text not found in {pdf.name}")
                doc.close()

# 5. Footer
st.markdown(f"""
    <div class="footer">
        Designed & Developed by <span style="color:#58a6ff; font-weight:bold;">Ahmed.Abdelmawgoud</span> | Senior Steel Coordinator © 2026
    </div>
""", unsafe_allow_html=True)
