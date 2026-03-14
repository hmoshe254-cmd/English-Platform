import streamlit as st
import os
import json

# ==========================================
# 1. إعدادات الصفحة الأساسية
# ==========================================
st.set_page_config(page_title="تعلم الإنجليزية بطلاقة", page_icon="🎓", layout="centered")

# ==========================================
# 2. قسم التصميم والأناقة (CSS)
# ==========================================
st.markdown("""
<style>
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
    .main-title { color: #4CAF50; text-align: center; direction: rtl; font-family: 'Tajawal', sans-serif;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. تجهيز المجلدات والملفات
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

# ==========================================
# 4. واجهة الطالب (الصفحة الرئيسية)
# ==========================================
st.markdown("<h1 class='main-title'>🎓 منصة إتقان اللغة الإنجليزية</h1>", unsafe_allow_html=True)
st.write("---")

for item in sentences:
    st.markdown(f"""
    <div class="sentence-card">
        <div class="eng-text">{item['english']}</div>
        <div class="ar-text">📖 <b>الترجمة:</b> {item['arabic']}</div>
        <div class="pron-text">🗣️ <b>النطق:</b> {item['pronunciation']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # الحل الجذري لمشكلة الآيفون (استخدام mpeg بدلاً من mp3)
    if os.path.exists(item['audio']):
        try:
            st.audio(item['audio'], format="audio/mpeg")
        except Exception as e:
            st.error("لا يمكن تشغيل الصوت")

# ==========================================
# 5. لوحة التحكم الجانبية (محمية برقم سري)
# ==========================================
with st.sidebar:
    st.markdown("<h3 style='text-align: right; direction: rtl;'>⚙️ لوحة الإدارة</h3>", unsafe_allow_html=True)
    
    secret_password = st.text_input("الرمز السري (12345):", type="password")
    
    if secret_password == "12345":
        st.success("🔓 تم الفتح!")
        bulk_text = st.text_area("انسخ الجمل هنا:", height=200)
        
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
                            os.system(f'edge-tts --text "{eng}" --voice "en-US-AriaNeural" --write-media "{audio_path}"')
                            
                            sentences.append({"english": eng, "arabic": ar, "pronunciation": pron, "audio": audio_path})
                            added_count += 1
            
            if added_count > 0:
                save_data(sentences)
                st.success(f"✅ تم إضافة {added_count} جملة!")
                st.rerun()
    elif secret_password != "":
        st.error("❌ الرمز السري خاطئ!")
