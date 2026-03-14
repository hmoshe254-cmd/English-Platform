import streamlit as st
import os
import json

# ==========================================
# 1. إعدادات الصفحة الأساسية
# ==========================================
st.set_page_config(page_title="منصة إتقان الإنجليزية", page_icon="🎓", layout="centered")

# ==========================================
# 2. تصميم احترافي (مسح الشريط الأبيض العلوي تماماً)
# ==========================================
st.markdown("""
<style>
    /* 🛑 إخفاء الشريط الأبيض العلوي (Fork, GitHub, Decoration) نهائياً */
    header {visibility: hidden !important; height: 0px !important;}
    [data-testid="stHeader"] {visibility: hidden !important; height: 0px !important;}
    [data-testid="stDecoration"] {display: none !important;}
    footer {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {visibility: hidden !important;}

    /* ضبط المسافة بالأعلى لتبدأ من الصفر */
    .block-container {padding-top: 0rem !important; padding-bottom: 1rem !important;}

    /* تصميم البطاقات (Dark Mode) الفخم */
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    
    body { background-color: #0e1117; } /* خلفية الموقع كاملة سوداء */
    
    .sentence-card { 
        direction: rtl; 
        background-color: #1e1e1e; 
        color: #ffffff; 
        border-radius: 15px; 
        padding: 20px; 
        margin-bottom: 20px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.5); 
        border-right: 6px solid #4CAF50; 
        text-align: right;
    }
    .eng-text { color: #64b5f6; font-size: 24px; font-weight: bold; direction: ltr; text-align: left; margin-bottom: 10px;}
    .ar-text { color: #e0e0e0; font-size: 18px; margin-bottom: 8px;}
    .pron-text { color: #ffb74d; font-size: 16px; }
    .main-title { color: #4CAF50; text-align: center; direction: rtl; font-size: 30px; font-weight: bold; padding-top: 20px;}
    
    /* جعل زر القائمة (الخطوط الثلاثة) بلون أخضر ليسهل رؤيته */
    [data-testid="stSidebarCollapsedControl"] {
        color: #4CAF50 !important;
        top: 20px !important;
    }
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
all_categories = sorted(list(set([s.get("category", "عام") for s in sentences] + ["عام"])))

# ==========================================
# 4. القائمة الجانبية (الأقسام + الإدارة)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: right; color:#4CAF50;'>📚 تصفح الأقسام</h2>", unsafe_allow_html=True)
    selected_category = st.selectbox("اختر القسم المراد دراسته:", all_categories)
    
    st.write("---")
    
    # تظهر فقط عند إضافة ?admin=true للرابط
    if st.query_params.get("admin") == "true":
        st.markdown("<h3 style='color:#ffb74d; text-align:right;'>🛠 لوحة الإدارة</h3>", unsafe_allow_html=True)
        cat_input = st.text_input("📂 اسم القسم الجديد:", "عام")
        bulk_text = st.text_area("أضف جملك (جملة | ترجمة | نطق):", height=150)
        
        if st.button("🚀 نشر الجمل بصوت رجل"):
            lines = bulk_text.strip().split('\n')
            for line in lines:
                if "|" in line:
                    parts = line.split("|")
                    eng, ar, pron = parts[0].strip(), parts[1].strip(), parts[2].strip()
                    
                    audio_path = f"audio/s_{len(sentences)}.mp3"
                    # استخدام صوت الرجل Guy
                    os.system(f'edge-tts --text "{eng}" --voice "en-US-GuyNeural" --write-media "{audio_path}"')
                    
                    sentences.append({
                        "english": eng, "arabic": ar, "pronunciation": pron, 
                        "audio": audio_path, "category": cat_input
                    })
            save_data(sentences)
            st.success("تم التحديث!")
            st.rerun()

# ==========================================
# 5. عرض الموقع للطلاب
# ==========================================
st.markdown("<h1 class='main-title'>🎓 منصة إتقان اللغة الإنجليزية</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#888;'>أنت الآن في قسم: {selected_category}</p>", unsafe_allow_html=True)

filtered = [s for s in sentences if s.get("category", "عام") == selected_category]

for item in filtered:
    st.markdown(f"""
    <div class="sentence-card">
        <div class="eng-text">{item['english']}</div>
        <div class="ar-text">📖 {item['arabic']}</div>
        <div class="pron-text">🗣️ النطق: {item['pronunciation']}</div>
    </div>
    """, unsafe_allow_html=True)
    if os.path.exists(item['audio']):
        st.audio(item['audio'])
