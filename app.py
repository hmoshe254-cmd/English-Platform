from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
import requests
import os

app = FastAPI()

# -------------------------
# DATABASE
# -------------------------

DATABASE_URL = "sqlite:///itqan.db"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Sentence(Base):

    __tablename__ = "sentences"

    id = Column(Integer, primary_key=True)
    english = Column(String)
    arabic = Column(String)
    pronunciation = Column(String)
    section = Column(String)
    audio = Column(String)

Base.metadata.create_all(engine)

# -------------------------
# STATIC FOLDER
# -------------------------

if not os.path.exists("audio"):
    os.makedirs("audio")

app.mount("/audio", StaticFiles(directory="audio"), name="audio")

# -------------------------
# AZURE TTS
# -------------------------

AZURE_KEY = "YOUR_AZURE_KEY"
AZURE_REGION = "eastus"

def generate_audio(text):

    filename = text.replace(" ","_")[:30]

    url = f"https://{AZURE_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_KEY,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3"
    }

    ssml = f"""
    <speak version='1.0' xml:lang='en-US'>
    <voice name='en-US-GuyNeural'>
    {text}
    </voice>
    </speak>
    """

    response = requests.post(url, headers=headers, data=ssml)

    path = f"audio/{filename}.mp3"

    with open(path,"wb") as f:
        f.write(response.content)

    return f"/audio/{filename}.mp3"

# -------------------------
# HOME PAGE
# -------------------------

@app.get("/", response_class=HTMLResponse)
def home():

    db = Session()

    sentences = db.query(Sentence).all()

    html = """
    <html>
    <head>
    <title>Itqan English</title>
    <style>

    body{
    background:#0e0e0e;
    color:white;
    font-family:Arial;
    padding:40px;
    }

    .card{
    border:1px solid #00aa66;
    padding:20px;
    margin-bottom:20px;
    border-radius:10px;
    background:#161616;
    }

    h2{
    color:#00ff99;
    }

    </style>
    </head>
    <body>

    <h1>منصة إتقان</h1>

    <a href='/admin'>لوحة الإدارة</a>

    """

    for s in sentences:

        html += f"""
        <div class='card'>

        <h2>{s.english}</h2>

        <p>{s.arabic}</p>

        <p>{s.pronunciation}</p>

        <audio controls>
        <source src='{s.audio}' type='audio/mpeg'>
        </audio>

        </div>
        """

    html += "</body></html>"

    return html

# -------------------------
# ADMIN PAGE
# -------------------------

@app.get("/admin", response_class=HTMLResponse)
def admin():

    return """

    <html>

    <body style="background:black;color:white;font-family:Arial;padding:40px">

    <h2>إضافة جملة</h2>

    <form method="post" action="/add">

    English sentence<br>
    <input name="english"><br><br>

    Arabic translation<br>
    <input name="arabic"><br><br>

    Arabic pronunciation<br>
    <input name="pronunciation"><br><br>

    Section<br>
    <input name="section"><br><br>

    <button type="submit">Add</button>

    </form>

    </body>
    </html>

    """

# -------------------------
# ADD SENTENCE
# -------------------------

@app.post("/add")
def add(

english: str = Form(...),
arabic: str = Form(...),
pronunciation: str = Form(...),
section: str = Form(...)

):

    db = Session()

    audio = generate_audio(english)

    s = Sentence(
        english=english,
        arabic=arabic,
        pronunciation=pronunciation,
        section=section,
        audio=audio
    )

    db.add(s)
    db.commit()

    return {"status":"added"}
