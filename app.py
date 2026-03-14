import streamlit as st
import os
import json

# ==========================================
# 1. إعدادات الصفحة والتصميم العصري
# ==========================================
st.set_page_config(page_title="منصة إتقان الإنجليزية", page_icon="🎓", layout="centered")

st.markdown("""
<style>
    /* إخفاء القطة والشريط العلوي وأي زوائد نهائياً */
    header, [data-testid="stHeader"], .stAppHeader, [data-testid="stToolbar"] {display: none !important; visibility: hidden !important;}
    footer {visibility: hidden !important;}
    [data-testid="stDecoration"] {display: none !important;}
    .stDeployButton {display: none !important;}
    
    /* رفع المحتوى للأعلى وتوسيطه */
    .block-container {padding-top: 0rem !important;}

    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    
    body { background-color: #0e1117; }
    
    /* تصميم البطاقات الاحترافي */
    .sentence-card { 
        direction: rtl; background-color: #1e1e1e; color: #ffffff; 
        border-radius: 15px; padding: 25px; margin-bottom: 20px; 
        box-shadow: 0 4px 20px rgba(0,0,0,0.6); border-right: 8px solid #4CAF50; text-align: right;
    }
    .eng-text { color: #64b5f6; font-size: 26px; font-weight: bold; direction: ltr; text-align: left; margin-bottom: 10px; }
    .ar-text { color: #e0e0e0; font-size: 19px; margin-bottom: 10px;}
    .pron-text { color: #ffb74d; font-size: 17px; background: rgba(255,183,77,0.1); padding: 5px 10px; border-radius: 8px; display: inline-block;}

    /* زر القائمة الجانبية (3 خطوط) بلون أخضر فاقع */
    [data-testid="stSidebarCollapsedControl"] { color: #4CAF50 !important; top: 15px !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. إدارة المجلدات والبيانات
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
# 3. القائمة الجانبية (الأقسام + لوحة الإدارة)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: right; color:#4CAF50;'>📚 تصفح الأقسام</h2>", unsafe_allow_html=True)
    selected_category = st.selectbox("اختر القسم الذي تريد دراسته:", all_categories)
    
    st.write("---")
    
    # تفعيل لوحة الإدارة عبر الرابط السري ?admin=true
    if st.query_params.get("admin") == "true":
        st.markdown("<h3 style='color:#ffb74d; text-align:right;'>🛠 لوحة تحكم المدير</h3>", unsafe_allow_html=True)
        
        # 1. خانة اسم القسم (هذه التي كنت تبحث عنها)
        new_cat = st.text_input("📂 الخطوة الأولى: اكتب اسم القسم هنا (مثلاً: الغرفة):", "عام")
        
        # 2. خانة لصق الجمل
        bulk_text = st.text_area("📝 الخطوة الثانية: الصق الجمل هنا (جملة | ترجمة | نطق):", height=200)
        
        if st.button("🚀 الخطوة الثالثة: نشر بصوت رجل"):
            lines = bulk_text.strip().split('\n')
            for line in lines:
                if "|" in line:
                    parts = line.split("|")
                    eng, ar, pron = parts[0].strip(), parts[1].strip(), parts[2].strip()
                    
                    audio_path = f"audio/s_{len(sentences)}.mp3"
                    # استخدام صوت الرجل Guy مع نطق احترافي 100%
                    os.system(f'edge-tts --text "{eng}" --voice "en-US-GuyNeural" --write-media "{audio_path}"')
                    
                    sentences.append({
                        "english": eng, "arabic": ar, "pronunciation": pron, 
                        "audio": audio_path, "category": new_cat
                    })
            save_data(sentences)
            st.success(f"تم بنجاح إضافة الجمل لقسم: {new_cat}")
            st.rerun()

# ==========================================
# 4. واجهة الطالب (نظيفة وعصرية)
# ==========================================
st.markdown("<h1 style='text-align:center; color:#4CAF50; font-size:35px;'>🎓 منصة إتقان الإنجليزية</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#888;'>أنت الآن تشاهد جمل قسم: <b>{selected_category}</b></p>", unsafe_allow_html=True)

filtered_data = [s for s in sentences if s.get("category", "عام") == selected_category]

if not filtered_data:
    st.info("هذا القسم فارغ حالياً، استخدم لوحة الإدارة لإضافة جمل.")

for item in filtered_data:
    st.markdown(f"""
    <div class="sentence-card">
        <div class="eng-text">{item['english']}</div>
        <div class="ar-text">📖 {item['arabic']}</div>
        <div class="pron-text">🗣️ نطق بالعربي: {item['pronunciation']}</div>
    </div>
    """, unsafe_allow_html=True)
    if os.path.exists(item['audio']):
        with open(item['audio'], "rb") as f:
            st.audio(f.read(), format="audio/mpeg")
