import streamlit as st
import os
import json
import subprocess

# ==========================================
# 1. إعدادات الصفحة
# ==========================================
st.set_page_config(page_title="منصة اللغة الإنجليزية", layout="centered")

# ==========================================
# 2. تصميم "الإبادة" (إخفاء كل شيء عدا زر الأقسام)
# ==========================================
st.markdown("""
<style>
    /* 🛑 إخفاء الشريط العلوي والقطة تماماً */
    [data-testid="stHeader"] {display: none !important;}
    header {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    footer {visibility: hidden !important;}
    
    /* 🟢 إظهار زر الخطوط الثلاثة (القائمة) وتلوينه بالأخضر */
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        color: #4CAF50 !important;
        background-color: rgba(76, 175, 80, 0.2) !important;
        border-radius: 50% !important;
        top: 15px !important;
        left: 15px !important;
        width: 45px !important;
        height: 45px !important;
    }

    /* تحسين البطاقات (Dark Mode) */
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
    .main-title { color: #4CAF50; text-align: center; padding-top: 20px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. إدارة البيانات
# ==========================================
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
# استخراج الأقسام لضمان ظهورها للطالب
all_categories = sorted(list(set([s.get("category", "عام") for s in sentences] + ["عام"])))

# ==========================================
# 4. القائمة الجانبية (الأقسام + لوحة الإدارة)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: right;'>📂 الأقسام</h2>", unsafe_allow_html=True)
    # تظهر للطالب ليختار القسم
    selected_category = st.radio("اختر القسم:", all_categories)
    
    st.write("---")
    
    # التحقق من رابط المدير (?admin=true)
    if st.query_params.get("admin") == "true":
        st.markdown("<h3 style='color:#ffb74d; text-align:right;'>🛠 لوحة الإدارة</h3>", unsafe_allow_html=True)
        
        # 📂 حقل الأقسام (سيظهر لك الآن 100%)
        category_name = st.text_input("اسم القسم (مثلاً: البيت):", value="عام")
        
        bulk_input = st.text_area("أضف الجمل (جملة | ترجمة | نطق):", height=150)
        
        if st.button("🚀 حفظ بصوت رجل"):
            lines = bulk_input.strip().split('\n')
            for line in lines:
                if "|" in line:
                    parts = line.split("|")
                    eng, ar, pron = parts[0].strip(), parts[1].strip(), parts[2].strip()
                    
                    # إنشاء ملف صوتي فريد
                    audio_filename = f"audio/m_{len(sentences)}_{eng[:5]}.mp3".replace(" ", "_")
                    
                    # ✨ الأمر الإجباري لصوت الرجل (Guy)
                    cmd = f'edge-tts --text "{eng}" --voice "en-US-GuyNeural" --write-media "{audio_filename}"'
                    os.system(cmd)
                    
                    sentences.append({
                        "english": eng, "arabic": ar, "pronunciation": pron, 
                        "audio": audio_filename, "category": category_name
                    })
            save_data(sentences)
            st.success("تم الحفظ! أعد تحميل الصفحة")
            st.rerun()

# ==========================================
# 5. عرض الموقع
# ==========================================
st.markdown("<h1 class='main-title'>🎓 منصة إتقان الإنجليزية</h1>", unsafe_allow_html=True)

filtered_data = [s for s in sentences if s.get("category", "عام") == selected_category]

for item in filtered_data:
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
