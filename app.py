import streamlit as st
import os
import json

# 1. إعدادات الصفحة
st.set_page_config(page_title="المنصة التعليمية", page_icon="🎓", layout="centered")

# 2. تصميم "الإبادة" للأشرطة البيضاء والقطة
st.markdown("""
<style>
    /* إخفاء كل شيء في الأعلى (القطة، الخطوط، Fork) */
    header, [data-testid="stHeader"], .stAppHeader {display: none !important; visibility: hidden !important;}
    [data-testid="stDecoration"] {display: none !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    
    /* رفع المحتوى للأعلى تماماً */
    .block-container {padding-top: 0rem !important;}

    /* تصميم البطاقات - لون غامق فخم */
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    .sentence-card { 
        direction: rtl; background-color: #1e1e1e; color: #ffffff; 
        border-radius: 15px; padding: 20px; margin-bottom: 20px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.5); border-right: 6px solid #4CAF50; text-align: right;
    }
    .eng-text { color: #64b5f6; font-size: 24px; font-weight: bold; direction: ltr; text-align: left; }
    .ar-text { color: #e0e0e0; font-size: 18px; }
    .pron-text { color: #ffb74d; font-size: 16px; }

    /* زر القائمة الجانبية للهواتف */
    [data-testid="stSidebarCollapsedControl"] { color: #4CAF50 !important; top: 10px !important; }
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

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

sentences = load_data()
all_categories = sorted(list(set([s.get("category", "عام") for s in sentences] + ["عام"])))

# 4. القائمة الجانبية (الأقسام + لوحة الإدارة)
with st.sidebar:
    st.markdown("<h2 style='text-align: right;'>📚 الأقسام</h2>", unsafe_allow_html=True)
    selected_category = st.selectbox("اختر القسم:", all_categories)
    
    st.write("---")
    
    # 🛑 تأكد أنك تستخدم رابط ينتهي بـ ?admin=true
    if st.query_params.get("admin") == "true":
        st.error("🛠 لوحة الإدارة مفعلة")
        
        # 📂 مربع الأقسام (تأكد من كتابة اسم القسم هنا قبل الحفظ)
        cat_input = st.text_input("📂 اكتب اسم القسم (المدرسة، البيت...):", "عام")
        
        bulk_text = st.text_area("الجمل (جملة | ترجمة | نطق):", height=150)
        
        if st.button("🚀 إضافة بصوت رجل"):
            lines = bulk_text.strip().split('\n')
            for line in lines:
                if "|" in line:
                    parts = line.split("|")
                    eng, ar, pron = parts[0].strip(), parts[1].strip(), parts[2].strip()
                    
                    audio_path = f"audio/m_{len(sentences)}.mp3"
                    # صوت الرجل Guy (أمريكي)
                    os.system(f'edge-tts --text "{eng}" --voice "en-US-GuyNeural" --write-media "{audio_path}"')
                    
                    sentences.append({
                        "english": eng, "arabic": ar, "pronunciation": pron, 
                        "audio": audio_path, "category": cat_input
                    })
            save_data(sentences)
            st.success("تم الحفظ!")
            st.rerun()

# 5. عرض الموقع
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
