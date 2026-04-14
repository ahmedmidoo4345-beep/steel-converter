import streamlit as st

# 1. إعدادات الصفحة والواجهة
st.set_page_config(
    page_title="Steel Coordinator Pro",
    page_icon="🏗️",
    layout="centered"
)

# 2. إضافة لمسة جمالية (CSS) لتنسيق التوقيع في الأسفل
footer_style = """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: #555;
        text-align: center;
        padding: 10px;
        font-family: 'Arial';
        font-size: 14px;
        border-top: 1px solid #e7e7e7;
    }
    </style>
    <div class="footer">
        <p>Created by <b>Ahmed.Abdelmawgoud</b> | Steel Coordination Tool v1.0</p>
    </div>
"""
st.markdown(footer_style, unsafe_allow_html=True)

# 3. عنوان البرنامج وشرحه
st.title("🏗️ Steel Coordinator Pro")
st.subheader("AutoCAD Version Converter")
st.write("الأداة الاحترافية لتحويل إصدارات الـ DWG الحديثة إلى إصدار **2007** لضمان التوافقية مع جميع الأجهزة.")

st.divider()

# 4. منطق البرنامج (المحرك)
TARGET_HEADER = b'AC1021' # كود إصدار 2007

uploaded_files = st.file_uploader("قم بسحب وإفلات ملفات الـ DWG هنا", type=['dwg'], accept_multiple_files=True)

if uploaded_files:
    st.write(f"### جاري المعالجة ({len(uploaded_files)}) ملفات...")
    
    # عمل أعمدة لعرض الملفات بشكل منظم
    for uploaded_file in uploaded_files:
        col1, col2 = st.columns([3, 1])
        
        # معالجة الملف
        file_bytes = uploaded_file.getvalue()
        modified_content = bytearray(file_bytes)
        modified_content[0:6] = TARGET_HEADER
        
        with col1:
            st.info(f"📄 {uploaded_file.name}")
        
        with col2:
            st.download_button(
                label="تحميل ✅",
                data=bytes(modified_content),
                file_name=f"Converted_{uploaded_file.name}",
                mime="application/octet-stream",
                key=uploaded_file.name # مفتاح فريد لكل زرار
            )

st.divider()
st.caption("ملاحظة: هذه الأداة تقوم بتغيير رقم الإصدار داخلياً لتمكين الفتح على النسخ القديمة.")
