import streamlit as st

# 1. إعدادات الصفحة والستايل
st.set_page_config(page_title="Steel Fixer Pro", page_icon="🏗️", layout="wide")

# كود CSS لتحسين المظهر (Custom UI)
st.markdown("""
    <style>
    /* تغيير لون الخلفية والعناوين */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    /* تنسيق صندوق الرفع */
    .stFileUploader {
        border: 2px dashed #4CAF50;
        border-radius: 15px;
        padding: 20px;
    }
    /* تنسيق التوقيع في الأسفل */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #161b22;
        color: #00d4ff;
        text-align: center;
        padding: 15px;
        font-family: 'Segoe UI';
        font-weight: bold;
        border-top: 2px solid #00d4ff;
        z-index: 100;
    }
    /* تأثير على الكروت */
    .file-card {
        background-color: #1c2128;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #00d4ff;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. الهيدر (Header)
col_title, col_logo = st.columns([4, 1])
with col_title:
    st.title("🏗️ Steel Coordinator Pro")
    st.markdown("<h3 style='color: #00d4ff;'>AutoCAD Recovery & Conversion Hub</h3>", unsafe_allow_html=True)
with col_logo:
    st.markdown("### 2026 Edition")

st.write("---")

# 3. واجهة البرنامج
st.write("📂 **ارفع ملفات الـ DWG الحديثة لتحويلها فوراً لنسخة 2013 المستقرة:**")

uploaded_files = st.file_uploader("", type=['dwg'], accept_multiple_files=True)

if uploaded_files:
    st.write(f"### ⚙️ جاري المعالجة الاحترافية ({len(uploaded_files)} ملف)...")
    
    # عرض الملفات في شبكة (Grid)
    cols = st.columns(2) # تقسيم الشاشة لعمودين للملفات
    
    for idx, uploaded_file in enumerate(uploaded_files):
        with cols[idx % 2]:
            st.markdown(f"""
                <div class="file-card">
                    <h4>📄 {uploaded_file.name}</h4>
                    <p style='color: #8b949e;'>Status: Ready for conversion to AC1027 (2013)</p>
                </div>
            """, unsafe_allow_html=True)
            
            # المعالجة (نفس الكود اللي نجح معاك)
            file_bytes = uploaded_file.getvalue()
            modified_content = bytearray(file_bytes)
            modified_content[0:6] = b'AC1027' # كود 2013 السحري
            
            # زرار تحميل شيك
            st.download_button(
                label=f"Download Fixed {uploaded_file.name} ✅",
                data=bytes(modified_content),
                file_name=f"Fixed_2013_{uploaded_file.name}",
                mime="application/octet-stream",
                key=f"btn_{idx}"
            )

# 4. التوقيع النهائي (The Signature)
st.markdown(f"""
    <div class="footer">
        Created with Precision by Ahmed.Abdelmawgoud | Senior Steel Coordinator 🛠️
    </div>
""", unsafe_allow_html=True)

# إضافة مساحة تحت عشان الفوتر ميتغطاش
st.write("<br><br><br>", unsafe_allow_html=True)
