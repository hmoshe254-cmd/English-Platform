import streamlit as st
import os
import json

# ==========================================
# 1. إعدادات الصفحة الأساسية
# ==========================================
st.set_page_config(page_title="تعلم الإنجليزية بطلاقة", page_icon="🎓", layout="centered")

# ==========================================
# 2. قسم التصميم والأناقة (CSS) - يمكنك تعديل الألوان من هنا مستقبلاً
# ==========================================
st.markdown("""
<style>
    /* استدعاء خط عربي أنيق من جوجل */
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: rtl; /* اتجاه الموقع من اليمين لليسار */
    }
    
    /* تصميم البطاقة التي تحتوي على الجملة */
    .sentence-card {
        background-color: #ffffff;
        border-radius: 15px; /* دائرية الحواف */
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); /* ظل خفيف */
        border-right: 6px solid #4CAF50; /* خط أخضر جانبي يعطي أناقة */
        transition: 0.3s; /* سرعة التأثير الحركي */
    }
    
    /* تأثير عند مرور الفأرة فوق البطاقة */
    .sentence-card:hover {
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        transform: translateY(-3px);
    }
    
    /* ألوان النصوص داخل البطاقة */
    .eng-text { color: #1E3A8A; font-size: 22px; font-weight: bold; margin-bottom: 5px; direction: ltr; text-align: left; }
    .ar-text { color: #333333; font-size: 18px; margin-bottom: 5px; }
    .pron-text { color: #E65100; font-size: 16px; }
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
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

sentences = load_data()

# ==========================================
# 4. واجهة الطالب (الصفحة الرئيسية)
# ==========================================
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🎓 منصة إتقان اللغة الإنجليزية</h1>", unsafe_allow_html=True)
st.write("---")

# عرض الجمل بتصميم البطاقات
for item in sentences:
    # استخدام HTML لإنشاء البطاقة بالتصميم الذي وضعناه بالأعلى
    st.markdown(f"""
    <div class="sentence-card">
        <div class="eng-text">{item['english']}</div>
        <div class="ar-text">📖 <b>الترجمة:</b> {item['arabic']}</div>
        <div class="pron-text">🗣️ <b>النطق:</b> {item['pronunciation']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # مشغل الصوت يظهر مباشرة تحت النص
    if os.path.exists(item['audio']):
        st.audio(item['audio'], format="audio/mp3")

# ==========================================
# 5. لوحة التحكم الجانبية (للمدير فقط)
# ==========================================
with st.sidebar:
    st.markdown("## ⚙️ لوحة الإدارة")
    st.write("أضف جملك هنا (الجملة | الترجمة | النطق):")
    
    bulk_text = st.text_area("الصق الجمل هنا:", height=200)
    
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
                        audio_path = f"audio/{len(sentences)}.mp3"
                        os.system(f'edge-tts --text "{eng}" --voice "en-US-AriaNeural" --write-media "{audio_path}"')
                        
                        sentences.append({"english": eng, "arabic": ar, "pronunciation": pron, "audio": audio_path})
                        added_count += 1
        
        if added_count > 0:
            save_data(sentences)
            st.success(f"✅ تم بنجاح إضافة {added_count} جملة جديدة!")
            st.rerun()
        else:
            st.warning("⚠️ يرجى التأكد من التنسيق أو أن الجمل غير مكررة.")