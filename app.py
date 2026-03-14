import streamlit as st
import os
import json

# 1. إعدادات الصفحة
st.set_page_config(page_title="منصة إتقان الإنجليزية", page_icon="🎓")

# 2. تصميم احترافي (إخفاء القطة والزوائد)
st.markdown("""
<style>
    header, [data-testid="stHeader"], footer {visibility: hidden !important; display: none !important;}
    .block-container {padding-top: 1rem !important;}
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    body { background-color: #0e1117; color: white; }
    .sentence-card { 
        direction: rtl; background-color: #1e1e1e; border-radius: 15px; 
        padding: 20px; margin-bottom: 20px; border-right: 6px solid #4CAF50; text-align: right;
    }
    .eng-text { color: #64b5f6; font-size: 24px; font-weight: bold; direction: ltr; text-align: left; }
</style>
""", unsafe_allow_html=True)

# 3. إدارة الملفات
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

# 4. واجهة الطالب (الأقسام)
st.markdown("<h1 style='text-align:center; color:#4CAF50;'>🎓 منصة إتقان الإنجليزية</h1>", unsafe_allow_html=True)

# اختيار القسم (موجود في الأعلى ليكون واضحاً)
selected_category = st.selectbox("📂 اختر القسم الذي تريد دراسته:", all_categories)

st.write("---")

# 5. لوحة الإدارة (ستظهر هنا في وسط الصفحة إذا استخدمت الرابط السري)
if st.query_params.get("admin") == "true":
    st.markdown("### 🛠 لوحة إضافة الجمل")
    
    # الخانة التي كنت تبحث عنها (اسم القسم)
    category_name = st.text_input("1️⃣ اكتب اسم القسم (مثلاً: الغرفة، المدرسة):", "عام")
    
    # خانة الجمل
    bulk_text = st.text_area("2️⃣ الصق الجمل هنا (الجملة | الترجمة | النطق):", height=150)
    
    if st.button("🚀 إضافة ونشر الآن"):
        lines = bulk_text.strip().split('\n')
        for line in lines:
            if "|" in line:
                parts = line.split("|")
                eng, ar, pron = parts[0].strip(), parts[1].strip(), parts[2].strip()
                audio_path = f"audio/v_{len(sentences)}.mp3"
                # توليد الصوت الرجالي
                os.system(f'edge-tts --text "{eng}" --voice "en-US-GuyNeural" --write-media "{audio_path}"')
                sentences.append({"english": eng, "arabic": ar, "pronunciation": pron, "audio": audio_path, "category": category_name})
        
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(sentences, f, ensure_ascii=False, indent=4)
        st.success(f"تمت إضافة الجمل لقسم: {category_name}")
        st.rerun()

# 6. عرض الجمل للطلاب
filtered = [s for s in sentences if s.get("category", "عام") == selected_category]
for item in filtered:
    st.markdown(f"""
    <div class="sentence-card">
        <div class="eng-text">{item['english']}</div>
        <div style="color:#e0e0e0;">📖 {item['arabic']}</div>
        <div style="color:#ffb74d;">🗣️ {item['pronunciation']}</div>
    </div>
    """, unsafe_allow_html=True)
    if os.path.exists(item['audio']):
        with open(item['audio'], "rb") as f:
            st.audio(f.read(), format="audio/mpeg")
