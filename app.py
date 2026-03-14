import streamlit as st
import os
import json

# ==========================================
# 1. إعدادات الصفحة الأساسية
# ==========================================
st.set_page_config(page_title="تعلم الإنجليزية بطلاقة", page_icon="🎓", layout="centered")

# ==========================================
# 2. قسم التصميم (تم إخفاء الإعلانات مع بقاء زر القائمة الجانبية)
# ==========================================
st.markdown("""
<style>
    /* إخفاء إعلانات Streamlit ولكن نحافظ على زر القائمة (الخطوط الثلاثة) */
    #MainMenu {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    
    /* رفع محتوى الموقع للأعلى */
    .block-container {padding-top: 2rem !important; padding-bottom: 1rem !important;}

    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    
    .sentence-card { 
        direction: rtl;
        background-color: #ffffff; 
        border-radius: 15px; 
        padding: 20px; 
        margin-bottom: 20px; 
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
        border-right: 6px solid #4CAF50; 
        transition: 0.3s; 
        text-align: right;
    }
    .sentence-card:hover { box-shadow: 0 8px 16px rgba(0,0,0,0.2); transform: translateY(-3px); }
    .eng-text { color: #1E3A8A; font-size: 22px; font-weight: bold; margin-bottom: 5px; direction: ltr; text-align: left; }
    .ar-text { color: #333333; font-size: 18px; margin-bottom: 5px; }
    .pron-text { color: #E65100; font-size: 16px; }
    .main-title { color: #4CAF50; text-align: center; direction: rtl; font-family: 'Tajawal', sans-serif; margin-bottom: 10px;}
    .category-title { color: #1E3A8A; text-align: center; font-size: 20px; margin-bottom: 30px; border-bottom: 2px solid #eeeeee; padding-bottom: 10px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. تجهيز المجلدات وقاعدة البيانات
# ==========================================
if not os.path.exists("audio"):
    os.makedirs("audio")

DATA_FILE = "sentences.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

sentences = load_data()

# استخراج كل الأقسام الموجودة بدون تكرار
all_categories = []
for s in sentences:
    cat = s.get("category", "عام")
    if cat not in all_categories:
        all_categories.append(cat)

if not all_categories:
    all_categories = ["عام"]

# ==========================================
# 4. القائمة الجانبية (للطالب وللمدير)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: right; direction: rtl;'>📚 أقسام التعلم</h2>", unsafe_allow_html=True)
    
    # قائمة التبويبات التي يختار منها الطالب
    selected_category = st.radio("اختر القسم:", all_categories)
    
    st.write("---")
    
    # لوحة الإدارة المخفية (بالرابط السري)
    if "admin" in st.query_params and st.query_params["admin"] == "true":
        st.markdown("<h3 style='text-align: right; direction: rtl; color: #E65100;'>⚙️ لوحة الإدارة</h3>", unsafe_allow_html=True)
        
        # حقل اسم القسم
        new_category = st.text_input("📂 اسم القسم (مثلاً: المدرسة، البيت):", "عام")
        
        bulk_text = st.text_area("انسخ الجمل هنا:", height=150)
        
        if st.button("🚀 إضافة ونشر"):
            lines = bulk_text.strip().split('\n')
            added_count = 0
            
            for line in lines:
                if "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        eng = parts[0].strip()
                        ar = parts[1].strip()
                        pron = parts[2].strip()
                        
                        if not any(s['english'] == eng for s in sentences):
                            audio_path = f"audio/s_{len(sentences)}.mp3"
                            
                            # ✨ التعديل هنا: تم تغيير الصوت إلى GuyNeural (صوت رجالي)
                            os.system(f'edge-tts --text "{eng}" --voice "en-US-GuyNeural" --write-media "{audio_path}"')
                            
                            sentences.append({
                                "english": eng, 
                                "arabic": ar, 
                                "pronunciation": pron, 
                                "audio": audio_path,
                                "category": new_category
                            })
                            added_count += 1
            
            if added_count > 0:
                save_data(sentences)
                st.success(f"✅ تم إضافة {added_count} جملة لقسم ({new_category})!")
                st.rerun()

# ==========================================
# 5. واجهة الطالب (عرض الجمل المفلترة)
# ==========================================
st.markdown("<h1 class='main-title'>🎓 منصة إتقان اللغة الإنجليزية</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='category-title'>📌 أنت تتصفح قسم: <b>{selected_category}</b></div>", unsafe_allow_html=True)

# عرض الجمل التي تنتمي للقسم المختار فقط
for item in sentences:
    if item.get("category", "عام") == selected_category:
        st.markdown(f"""
        <div class="sentence-card">
            <div class="eng-text">{item['english']}</div>
            <div class="ar-text">📖 <b>الترجمة:</b> {item['arabic']}</div>
            <div class="pron-text">🗣️ <b>النطق:</b> {item['pronunciation']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if os.path.exists(item['audio']):
            try:
                with open(item['audio'], "rb") as audio_file:
                    audio_bytes = audio_file.read()
                st.audio(audio_bytes, format="audio/mpeg")
            except Exception as e:
                st.error("حدث خطأ في قراءة ملف الصوت.")
