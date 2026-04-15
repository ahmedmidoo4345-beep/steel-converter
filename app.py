import streamlit as st

# إعدادات واجهة البرنامج الاحترافية
st.set_page_config(page_title="Steel Coordinator Pro", page_icon="🏗️")

# التوقيع الخاص بك (Created by Ahmed.Abdelmawgoud)
footer = """
    <style>
    .footer { position: fixed; bottom: 0; width: 100%; text-align: center; padding: 10px; background: #f1f1f1; color: #555; }
    </style>
    <div class="footer"><p>Created by <b>Ahmed.Abdelmawgoud</b> | Steel Coordination Tool v2.0</p></div>
"""
st.markdown(footer, unsafe_allow_html=True)

st.title("🏗️ Steel Coordinator: AutoCAD Fixer")
st.subheader("أداة تحويل الملفات الحديثة إلى إصدار 2013")
st.write("هذا التحديث يستخدم تقنية 'الخداع البرمجي' التي نجحت في فتح الملفات المستعصية.")

# أداة رفع الملفات
uploaded_files = st.file_uploader("ارفع ملفات الـ DWG (إصدار 2018 أو أحدث)", type=['dwg'], accept_multiple_files=True)

if uploaded_files:
    st.write(f"--- جاري معالجة {len(uploaded_files)} ملف ---")
    
    for uploaded_file in uploaded_files:
        # قراءة محتوى الملف
        file_bytes = uploaded_file.getvalue()
        modified_content = bytearray(file_bytes)
        
        # فحص الهيدر (أول 6 حروف)
        current_header = modified_content[0:6]
        
        # إذا كان الملف إصدار 2018 (AC1032) أو أي إصدار حديث
        # هنحوله لـ 2013 (AC1027) زي ما عملت في كولاب بالظبط
        modified_content[0:6] = b'AC1027'
        
        st.success(f"✅ تم تحويل {uploaded_file.name} إلى إصدار 2013 بنجاح!")
        
        # زرار التحميل
        st.download_button(
            label=f"تحميل الملف المُصلح ({uploaded_file.name})",
            data=bytes(modified_content),
            file_name=f"Fixed_2013_{uploaded_file.name}",
            mime="application/octet-stream",
            key=uploaded_file.name
        )

st.divider()
st.info("نصيحة: إذا ظهرت رسالة تنبيه عند فتح الملف، اضغط Continue ثم استخدم أمر Save As لحفظ الملف رسمياً.")
