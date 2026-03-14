import streamlit as st
import json
import os
import asyncio
import edge_tts
import base64
from datetime import datetime

# --- إعدادات الصفحة الأساسية ---
st.set_page_config(page_title="منصة إتقان الإنجليزية", layout="wide", initial_sidebar_state="expanded")

# --- ملف تخزين البيانات ---
DB_FILE = 'data_store.json'
AUDIO_DIR = 'audio_files'

if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- محرك النطق (Edge TTS) ---
async def generate_voice(text, filename):
    communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
    await communicate.save(os.path.join(AUDIO_DIR, filename))

def get_audio_html(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        return f'<audio controls style="width: 100%; height: 40px;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'

# --- إخفاء عناصر Streamlit (CSS القوي) ---
hide_st_style = """
            <style>
            /* إخفاء الهيدر والقائمة والماركة */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display:none;}
            [data-testid="stToolbar"] {visibility: hidden !important;}
            
            /* تصميم الخلفية والوضع الداكن */
            .stApp {
                background-color: #000000;
                color: #ffffff;
            }
            
            /* تصميم البطاقات الإحترافي */
            .english-card {
                background-color: #1E1E1E;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 15px;
                border-left: 5px solid #28a745;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            }
            .en-text { font-size: 24px; font-weight: bold; color: #ffffff; margin-bottom: 5px; }
            .ar-text { font-size: 18px; color: #b0b0b0; direction: rtl; }
            .pron-text { font-size: 16px; color: #28a745; font-style: italic; }
            
            /* تعديل القائمة الجانبية */
            section[data-testid="stSidebar"] {
                background-color: #111111;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- منطق لوحة التحكم (Hidden Admin Panel) ---
query_params = st.query_params
is_admin = query_params.get("admin") == "true"

data = load_data()

if is_admin:
    st.title("🛠 لوحة الإدارة السرية")
    with st.expander("إضافة قسم أو جمل جديدة", expanded=True):
        new_cat = st.text_input("اسم القسم الجديد (مثلاً: المطار)")
        batch_input = st.text_area("أدخل الجمل بتنسيق: (الجملة | الترجمة | النطق العربي)", help="مثال: Hello | مرحباً | هالو")
        
        if st.button("حفظ البيانات وتوليد الصوت"):
            if new_cat and batch_input:
                if new_cat not in data:
                    data[new_cat] = []
                
                lines = batch_input.split('\n')
                progress_bar = st.progress(0)
                
                for i, line in enumerate(lines):
                    if '|' in line:
                        en, ar, pr = map(str.strip, line.split('|'))
                        audio_filename = f"{en[:10]}_{datetime.now().timestamp()}.mp3".replace(" ", "_")
                        
                        # توليد الصوت
                        asyncio.run(generate_voice(en, audio_filename))
                        
                        data[new_cat].append({
                            "en": en,
                            "ar": ar,
                            "pr": pr,
                            "audio": audio_filename
                        })
                
                save_data(data)
                st.success(f"تم تحديث قسم {new_cat} بنجاح!")
                st.rerun()

# --- واجهة المستخدم (Student UI) ---
st.sidebar.title("📚 الأقسام")
if data:
    category = st.sidebar.radio("اختر التصنيف:", list(data.keys()))

    st.markdown(f"<h2 style='text-align: center; color: #28a745;'>{category}</h2>", unsafe_allow_html=True)
    
    for item in data[category]:
        with st.container():
            st.markdown(f"""
            <div class="english-card">
                <div class="en-text">{item['en']}</div>
                <div class="ar-text">{item['ar']}</div>
                <div class="pron-text">النطق: {item['pr']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # عرض مشغل الصوت
            audio_path = os.path.join(AUDIO_DIR, item['audio'])
            if os.path.exists(audio_path):
                st.markdown(get_audio_html(audio_path), unsafe_allow_html=True)
            st.markdown("---")
else:
    st.info("مرحباً بك! سيظهر المحتوى هنا بمجرد إضافة البيانات من قبل الإدارة.")
