import streamlit as st
import fitz  # PyMuPDF
import io

# 1. Page Configuration
st.set_page_config(page_title="SteelFixer Precision", page_icon="🏗️", layout="wide")

# 2. Premium Styling
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .main-title { color: #58a6ff; text-align: center; font-weight: 800; font-size: 2.5rem; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #010409; text-align: center; padding: 10px; color: #8b949e; border-top: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# 3. Header & Navigation
st.markdown("<h1 class='main-title'>🏗️ STEEL COORDINATOR PRECISION</h1>", unsafe_allow_html=True)

col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    dwg_mode = st.button("📂 AutoCAD Version Fixer", use_container_width=True)
with col_nav2:
    pdf_mode = st.button("📝 PDF Smart Replacer", use_container_width=True)

if 'mode' not in st.session_state: st.session_state.mode = 'dwg'
if dwg_mode: st.session_state.mode = 'dwg'
if pdf_mode: st.session_state.mode = 'pdf'

st.write("---")

# --- MODE 2: PDF REPLACER (With Advanced Font Handling) ---
if st.session_state.mode == 'pdf':
    st.subheader("High-Precision PDF Text Replacement")
    
    with st.expander("🛠️ Advanced Font Settings (Optional)"):
        selected_font = st.selectbox("Select Font Style to match your drawing:", 
                                   ["helv", "cour", "tirom", "zapfdingbats"], 
                                   help="helv = Standard, cour = Mono/Technical, tirom = Serif")
        font_weight = st.slider("Fine-tune Font Size Adjustment:", 0.5, 1.5, 1.0)

    c1, c2 = st.columns(2)
    with c1: find_txt = st.text_input("FIND WHAT:")
    with c2: replace_txt = st.text_input("REPLACE WITH:")
        
    pdf_files = st.file_uploader("Upload PDF Drawings", type=['pdf'], accept_multiple_files=True)

    if pdf_files and find_txt and replace_txt:
        if st.button("Execute Precision Replacement"):
            for pdf in pdf_files:
                doc = fitz.open(stream=pdf.read(), filetype="pdf")
                modified = False
                
                for page in doc:
                    text_instances = page.search_for(find_txt)
                    for rect in text_instances:
                        # 1. Capture exact Style
                        dict_info = page.get_text("dict", clip=rect)
                        try:
                            span = dict_info["blocks"][0]["lines"][0]["spans"][0]
                            orig_size = span["size"] * font_weight # Apply manual fine-tuning
                            orig_color = span["color"]
                            r = (orig_color >> 16) & 0xFF
                            g = (orig_color >> 8) & 0xFF
                            b = orig_color & 0xFF
                            rgb_color = (r/255, g/255, b/255)
                        except:
                            orig_size = 10
                            rgb_color = (0, 0, 0)

                        # 2. Clean Area
                        page.add_redact_annot(rect, fill=(1, 1, 1))
                        page.apply_redactions()
                        
                        # 3. Insert Text with "Overlay" logic
                        # We use 'render_mode=0' to ensure it's not blurry
                        page.insert_text(fitz.Point(rect.x0, rect.y1 - (orig_size * 0.2)), 
                                        replace_txt, 
                                        fontsize=orig_size, 
                                        color=rgb_color,
                                        fontname=selected_font)
                        modified = True
                
                if modified:
                    out = io.BytesIO()
                    doc.save(out, garbage=3, deflate=True)
                    st.success(f"Success: {pdf.name}")
                    st.download_button(f"Download {pdf.name}", data=out.getvalue(), file_name=f"Fixed_{pdf.name}")
                doc.close()

# --- MODE 1: DWG FIXER ---
else:
    st.subheader("AutoCAD Version Recovery")
    dwg_files = st.file_uploader("Upload DWG files", type=['dwg'], accept_multiple_files=True)
    if dwg_files:
        for dwg in dwg_files:
            content = bytearray(dwg.getvalue())
            content[0:6] = b'AC1027'
            st.download_button(f"Download Fixed {dwg.name}", data=bytes(content), file_name=f"Fixed_{dwg.name}")

st.markdown(f"<div class='footer'>Created by Ahmed.Abdelmawgoud | Engineering Excellence</div>", unsafe_allow_html=True)
