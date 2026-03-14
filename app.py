import streamlit as st
import os
import json

# ==========================================
# 1. إعدادات الصفحة الأساسية
# ==========================================
st.set_page_config(page_title="منصة تعلم الإنجليزية", page_icon="🎓", layout="centered")

# ==========================================
# 2. قسم التصميم (إجبار إظهار القائمة الجانبية)
# ==========================================
st.markdown("""
<style>
    /* إخفاء القوائم غير الضرورية مع الحفاظ على زر القائمة الجانبية (الخطوط الثلاثة) */
    footer {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    
    /* جعل زر القائمة الجانبية (الخطوط الثلاثة) ظاهراً وواضحاً في الهواتف */
    [data-testid="stHeader"] { background-color: rgba(255,255,255,0.9); }
    
    /* تحسين شكل بطاقات الجمل */
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    
    .sentence-card { 
        direction: rtl; background-color: #ffffff; border-radius: 15px; 
        padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
        border-right: 6px solid #4CAF50; text-align: right;
    }
    .eng-text { color: #1E3A8A; font-size: 22px; font-weight: bold; direction: ltr; text-align: left; }
    .ar-text { color: #333333; font-size: 18px; }
    .pron-text { color: #E65100; font-size: 16px; }
    .main-title { color: #4CAF50; text-align: center; direction: rtl; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. إدارة البيانات والملفات
# ==========================================
if not os.path.exists("audio"):
    os.makedirs("audio")

DATA_FILE = "sentences.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

sentences = load_data()

# استخراج الأقسام
all_categories = sorted(list(set([s.get("category", "عام") for s in sentences] + ["عام"])))

# ==========================================
# 4. القائمة الجانبية (التي ستظهر للطلاب كـ 3 خطوط)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: right;'>📚 الأقسام</h2>", unsafe_allow_html=True)
    # الطالب يختار القسم من هنا
    selected_category = st.selectbox("اختر المكان أو التصنيف:", all_categories)
    
    st.write("---")
    
    # لوحة المدير (تظهر فقط عند إضافة ?admin=true للرابط)
    if st.query_params.get("admin") == "true":
        st.markdown("<h3 style='color:red; text-align:right;'>🛠 لوحة التحكم</h3>", unsafe_allow_html=True)
        
        # 🟢 هذا هو "مربع الأقسام" الذي طلبته يا محمد
        cat_input = st.text_input("📂 اكتب اسم القسم هنا (مثلاً: البيت):", "عام")
        
        bulk_text = st.text_area("انسخ الجمل هنا (جملة | ترجمة | نطق):", height=150)
        
        if st.button("✅ حفظ ونشر بصوت رجل"):
            lines = bulk_text.strip().split('\n')
            for line in lines:
                if "|" in line:
                    parts = line.split("|")
                    eng, ar, pron = parts[0].strip(), parts[1].strip(), parts[2].strip()
                    
                    audio_path = f"audio/s_{len(sentences)}.mp3"
                    # ✨ استخدام صوت الرجل (Guy)
                    os.system(f'edge-tts --text "{eng}" --voice "en-US-GuyNeural" --write-media "{audio_path}"')
                    
                    sentences.append({
                        "english": eng, "arabic": ar, "pronunciation": pron, 
                        "audio": audio_path, "category": cat_input
                    })
            save_data(sentences)
            st.success("تم الإضافة بنجاح!")
            st.rerun()

# ==========================================
# 5. عرض الجمل
# ==========================================
st.markdown("<h1 class='main-title'>🎓 منصة تعلم الإنجليزية</h1>", unsafe_allow_html=True)
st.info(f"عرض جمل قسم: {selected_category}")

filtered_sentences = [s for s in sentences if s.get("category", "عام") == selected_category]

for item in filtered_sentences:
    st.markdown(f"""
    <div class="sentence-card">
        <div class="eng-text">{item['english']}</div>
        <div class="ar-text">📖 {item['arabic']}</div>
        <div class="pron-text">🗣️ {item['pronunciation']}</div>
    </div>
    """, unsafe_allow_html=True)
    if os.path.exists(item['audio']):
        st.audio(item['audio'])
