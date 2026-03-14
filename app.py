import streamlit as st
import os
import json

# 1. إعدادات الصفحة
st.set_page_config(page_title="منصة إتقان الإنجليزية", page_icon="🎓", layout="centered")

# 2. تصميم احترافي (إخفاء القطة والزوائد تماماً)
st.markdown("""
<style>
    header, [data-testid="stHeader"], footer, .stAppHeader {display: none !important; visibility: hidden !important;}
    [data-testid="stDecoration"], .stDeployButton, [data-testid="stToolbar"] {display: none !important;}
    .block-container {padding-top: 2rem !important;}
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    body { background-color: #0e1117; color: white; }
    .sentence-card { 
        direction: rtl; background-color: #1e1e1e; border-radius: 15px; 
        padding: 25px; margin-bottom: 20px; border-right: 8px solid #4CAF50; text-align: right;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .eng-text { color: #64b5f6; font-size: 26px; font-weight: bold; direction: ltr; text-align: left; margin-bottom: 10px;}
    .ar-text { color: #e0e0e0; font-size: 19px; }
    .pron-text { color: #ffb74d; font-size: 17px; background: rgba(255,183,77,0.1); padding: 5px; border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

# 3. إدارة البيانات
if not os.path.exists("audio"): os.makedirs("audio")
DATA_FILE = "sentences.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return []
    return []

sentences = load_data()
all_categories = sorted(list(set([s.get("category", "عام") for s in sentences] + ["عام"])))

# 4. واجهة الطالب (العنوان واختيار القسم)
st.markdown("<h1 style='text-align:center; color:#4CAF50;'>🎓 منصة إتقان اللغة الإنجليزية</h1>", unsafe_allow_html=True)

# 5. 🛠 لوحة الإدارة (ستظهر هنا في قلب الصفحة للمدير فقط)
if st.query_params.get("admin") == "true":
    with st.expander("🛠 لوحة التحكم - إضافة جمل جديدة", expanded=True):
        st.warning("أهلاً بك يا محمد في لوحة الإدارة")
        
        # ⭐ هذه هي الخانة المطلوبة - ستظهر هنا إجبارياً
        new_cat_name = st.text_input("📂 1. اكتب اسم القسم (مثلاً: الغرفة):", "عام")
        
        bulk_input = st.text_area("📝 2. الصق الجمل هنا (جملة | ترجمة | نطق):", height=150)
        
        if st.button("🚀 3. حفظ ونشر بصوت رجل"):
            lines = bulk_input.strip().split('\n')
            for line in lines:
                if "|" in line:
                    parts = line.split("|")
                    eng, ar, pron = parts[0].strip(), parts[1].strip(), parts[2].strip()
                    audio_path = f"audio/v_{len(sentences)}.mp3"
                    # صوت الرجل Guy
                    os.system(f'edge-tts --text "{eng}" --voice "en-US-GuyNeural" --write-media "{audio_path}"')
                    sentences.append({"english": eng, "arabic": ar, "pronunciation": pron, "audio": audio_path, "category": new_cat_name})
            
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(sentences, f, ensure_ascii=False, indent=4)
            st.success(f"تمت إضافة الجمل لقسم: {new_cat_name}")
            st.rerun()

st.write("---")

# اختيار القسم للطالب
selected_category = st.selectbox("📂 اختر القسم الذي تريد دراسته:", all_categories)

# 6. عرض الجمل
filtered = [s for s in sentences if s.get("category", "عام") == selected_category]
for item in filtered:
    st.markdown(f"""
    <div class="sentence-card">
        <div class="eng-text">{item['english']}</div>
        <div class="ar-text">📖 {item['arabic']}</div>
        <div class="pron-text">🗣️ نطق: {item['pronunciation']}</div>
    </div>
    """, unsafe_allow_html=True)
    if os.path.exists(item['audio']):
        with open(item['audio'], "rb") as f:
            st.audio(f.read(), format="audio/mpeg")
