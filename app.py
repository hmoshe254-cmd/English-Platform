import streamlit as st
import os
import json

# 1. إعدادات الصفحة والتصميم
st.set_page_config(page_title="منصة إتقان الإنجليزية", page_icon="🎓")

st.markdown("""
<style>
    header, [data-testid="stHeader"], footer, [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    .block-container {padding-top: 0rem !important;}
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    body { background-color: #0e1117; }
    .sentence-card { 
        direction: rtl; background-color: #1e1e1e; color: #ffffff; 
        border-radius: 15px; padding: 25px; margin-bottom: 20px; 
        box-shadow: 0 4px 20px rgba(0,0,0,0.6); border-right: 8px solid #4CAF50; text-align: right;
    }
    .eng-text { color: #64b5f6; font-size: 26px; font-weight: bold; direction: ltr; text-align: left; }
    .ar-text { color: #e0e0e0; font-size: 19px; }
    .pron-text { color: #ffb74d; font-size: 17px; background: rgba(255,183,77,0.1); padding: 5px; border-radius: 8px;}
    [data-testid="stSidebarCollapsedControl"] { color: #4CAF50 !important; }
</style>
""", unsafe_allow_html=True)

# 2. إدارة البيانات
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

# 3. القائمة الجانبية (الأقسام + لوحة الإدارة)
with st.sidebar:
    st.markdown("<h2 style='text-align: right;'>📚 الأقسام</h2>", unsafe_allow_html=True)
    selected_category = st.selectbox("اختر القسم:", all_categories)
    
    st.write("---")
    
    # لوحة الإدارة (تظهر فقط عند وجود ?admin=true)
    if st.query_params.get("admin") == "true":
        st.markdown("<h3 style='color:#4CAF50;'>🛠 لوحة التحكم</h3>", unsafe_allow_html=True)
        
        # 📂 خانة اسم القسم - أضفتها هنا بوضوح
        category_name = st.text_input("1️⃣ اسم القسم (مثلاً: الغرفة):", "عام")
        
        bulk_text = st.text_area("2️⃣ الصق الجمل هنا (جملة | ترجمة | نطق):", height=200)
        
        if st.button("🚀 حفظ ونشر بصوت رجل"):
            lines = bulk_text.strip().split('\n')
            for line in lines:
                if "|" in line:
                    p = line.split("|")
                    audio_path = f"audio/v_{len(sentences)}.mp3"
                    os.system(f'edge-tts --text "{p[0]}" --voice "en-US-GuyNeural" --write-media "{audio_path}"')
                    sentences.append({
                        "english": p[0], "arabic": p[1], "pronunciation": p[2], 
                        "audio": audio_path, "category": category_name
                    })
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(sentences, f, ensure_ascii=False, indent=4)
            st.success(f"تمت إضافة الجمل لقسم {category_name}")
            st.rerun()

# 4. الواجهة
st.markdown("<h1 style='text-align:center; color:#4CAF50;'>🎓 منصة إتقان الإنجليزية</h1>", unsafe_allow_html=True)

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
