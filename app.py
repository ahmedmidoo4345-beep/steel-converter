import streamlit as st
import fitz  # PyMuPDF
import io

# 1. Page Configuration
st.set_page_config(page_title="SteelFixer Master", page_icon="🏗️", layout="wide")

# 2. Ultra-Premium Styling
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .main-title { color: #58a6ff; text-align: center; font-weight: 800; font-size: 2.5rem; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #010409; text-align: center; padding: 10px; color: #8b949e; border-top: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# 3. Header & Navigation
st.markdown("<h1 class='main-title'>🏗️ STEEL COORDINATOR MASTER</h1>", unsafe_allow_html=True)

col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    dwg_mode = st.button("📂 AutoCAD Version Fixer", use_container_width=True)
with col_nav2:
    pdf_mode = st.button("📝 PDF Smart Replacer", use_container_width=True)

if 'mode' not in st.session_state: st.session_state.mode = 'dwg'
if dwg_mode: st.session_state.mode = 'dwg'
if pdf_mode: st.session_state.mode = 'pdf'

st.write("---")

# --- MODE 2: PDF REPLACER (The Master Logic) ---
if st.session_state.mode == 'pdf':
    st.subheader("Master-Precision Text Replacement")
    st.write("Replacing text while preserving the original engineering layout and style.")
    
    with st.expander("🎨 Visual Fine-Tuning"):
        font_selection = st.selectbox("Font Type:", ["helv", "cour", "tirom"], index=1, help="Use 'cour' (Courier) for CAD-like monospaced fonts.")
        y_offset = st.slider("Vertical Alignment Offset:", -5.0, 5.0, 0.0, help="Adjust if text is too high or low.")
        bold_effect = st.checkbox("Apply Bold Effect", value=False)

    c1, c2 = st.columns(2)
    with c1: find_txt = st.text_input("FIND WHAT (e.g. T-L-131-380MFTR-0034):")
    with c2: replace_txt = st.text_input("REPLACE WITH:")
        
    pdf_files = st.file_uploader("Upload PDF Drawings", type=['pdf'], accept_multiple_files=True)

    if pdf_files and find_txt and replace_txt:
        if st.button("Execute Master Replacement"):
            for pdf in pdf_files:
                doc = fitz.open(stream=pdf.read(), filetype="pdf")
                modified = False
                
                for page in doc:
                    # Search for text with metadata
                    blocks = page.get_text("dict")["blocks"]
                    for b in blocks:
                        if "lines" in b:
                            for l in b["lines"]:
                                for s in l["spans"]:
                                    if find_txt in s["text"]:
                                        # Capture Original Metrics
                                        orig_size = s["size"]
                                        orig_color = s["color"]
                                        # Get Origin point (The precise baseline start)
                                        origin_x, origin_y = s["origin"]
                                        
                                        # RGB Color conversion
                                        r = (orig_color >> 16) & 0xFF
                                        g = (orig_color >> 8) & 0xFF
                                        b_color = orig_color & 0xFF
                                        rgb = (r/255, g/255, b_color/255)

                                        # Redact the exact span area
                                        page.add_redact_annot(s["bbox"], fill=(1, 1, 1))
                                        page.apply_redactions()
                                        
                                        # Insert New Text using the exact Origin point
                                        page.insert_text(
                                            fitz.Point(origin_x, origin_y + y_offset), 
                                            replace_txt, 
                                            fontsize=orig_size, 
                                            color=rgb,
                                            fontname=font_selection,
                                            render_mode=1 if bold_effect else 0 # 1 is outline (bold)
                                        )
                                        modified = True
                
                if modified:
                    out = io.BytesIO()
                    doc.save(out, garbage=3, deflate=True)
                    st.success(f"Success: {pdf.name}")
                    st.download_button(f"Download Fixed {pdf.name}", data=out.getvalue(), file_name=f"Modified_{pdf.name}")
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

st.markdown(f"<div class='footer'>Created by Ahmed.Abdelmawgoud | Engineering Intelligence © 2026</div>", unsafe_allow_html=True)
