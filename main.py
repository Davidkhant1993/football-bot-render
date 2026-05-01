import time
import asyncio
import threading
import requests
import schedule
from datetime import datetime
from flask import Flask
from telegram import Bot


# =========================================================
# RENDER WEB SERVER
# =========================================================
app = Flask(__name__)

@app.route("/")
def home():
    return "Football Bot Running"


def run_web():
    app.run(host="0.0.0.0", port=10000)


threading.Thread(target=run_web).start()


# =========================================================
# EDIT ONLY THESE 2 VALUES
# =========================================================
BOT_TOKEN = "8498955364:AAHlm0z49sMNxcQUqIaMOnM9evizJUMnl8A"
CHANNEL_ID = "@Manchesterunitedfanbased"


# =========================================================
# SETTINGS
# =========================================================
SEND_ON_START = True
DAILY_POST_TIME = "10:00"
MATCH_LIMIT = 5


bot = Bot(token=BOT_TOKEN)


# =========================================================
# FREE DATA SOURCE - SCOREBAT
# =========================================================
def get_matches():
    try:
        url = "https://www.scorebat.com/video-api/v3/"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("response", [])[:MATCH_LIMIT]
    except Exception as e:
        print(f"Get matches error: {e}", flush=True)
        return []


def clean_competition(comp):
    if isinstance(comp, dict):
        return comp.get("name", "Football")
    return str(comp)


def build_analysis(title):
    title_lower = title.lower()

    if "manchester united" in title_lower or "man united" in title_lower:
        return "Man United ဘက်က attacking transition နဲ့ wing play ကိုအဓိကအားထားနိုင်ပြီး defensive concentration က အရေးကြီးနိုင်ပါတယ်။"

    if "real madrid" in title_lower or "barcelona" in title_lower:
        return "Big match pressure ကြောင့် midfield control နဲ့ counter attack timing က result ကိုဆုံးဖြတ်နိုင်ပါတယ်။"

    if "arsenal" in title_lower or "liverpool" in title_lower:
        return "High pressing နှစ်သင်းဖြစ်နိုင်ပြီး tempo မြန်တဲ့ open game ဖြစ်နိုင်ပါတယ်။"

    return "နှစ်သင်းလုံးအတွက် momentum အရေးကြီးပြီး first goal ရတဲ့ဘက်က game control ပိုရနိုင်ပါတယ်။"


def build_tip(title):
    title_lower = title.lower()

    if "real madrid" in title_lower or "barcelona" in title_lower:
        return "BTTS / Over 1.5 Goals angle စဉ်းစားလို့ရပါတယ်။"

    if "manchester united" in title_lower:
        return "Over 1.5 Goals angle စဉ်းစားလို့ရပါတယ်။"

    return "Balanced match ဖြစ်နိုင်ပြီး Over 1.5 Goals angle စဉ်းစားလို့ရပါတယ်။"


def build_post(match):
    title = match.get("title", "Football Match")
    competition = clean_competition(match.get("competition", "Football"))
    date = match.get("date", "Unknown Time")

    analysis = build_analysis(title)
    tip = build_tip(title)

    text = ""
    text += "🔥 MATCH PREVIEW\n"
    text += "━━━━━━━━━━━━━━\n"
    text += f"⚽ {title}\n"
    text += f"🏆 {competition}\n"
    text += f"🕒 {date}\n\n"

    text += "📊 Match Status\n"
    text += "Upcoming / Recent football match data\n\n"

    text += "📈 Recent Performance\n"
    text += "Free source မှာ detailed form data မပါသေးပါ\n\n"

    text += "🚑 Injury Update\n"
    text += "Official injury data မရသေးပါ\n\n"

    text += "👥 Expected Lineup\n"
    text += "Official lineup မထွက်သေးပါ / Free source မှာ lineup data မပါသေးပါ\n\n"

    text += "🧠 Match Analysis\n"
    text += analysis + "\n\n"

    text += "🎯 Prediction Tip\n"
    text += tip + "\n\n"

    text += "⚠️ Note: Betting signal မဟုတ်ပါ။ Free football source အခြေခံပြီး preview ရေးထားတာပါ။\n\n"

    text += "#Football #MatchPreview"

    return text


def send_message(text):
    asyncio.run(
        bot.send_message(
            chat_id=CHANNEL_ID,
            text=text
        )
    )


def send_posts():
    print("Building football posts...", flush=True)

    matches = get_matches()
    print(f"Matches found: {len(matches)}", flush=True)

    if not matches:
        send_message("⚠️ Match data မတွေ့သေးပါ။ နောက်တစ်ကြိမ် auto စစ်ပါမယ်။")
        return

    for match in matches:
        try:
            text = build_post(match)
            send_message(text)
            print("Post sent", flush=True)
            time.sleep(2)
        except Exception as e:
            print(f"Send error: {e}", flush=True)

    print("Done", flush=True)


# =========================================================
# RUN
# =========================================================
if SEND_ON_START:
    send_posts()

schedule.every().day.at(DAILY_POST_TIME).do(send_posts)

print("Football Bot Running...", flush=True)

while True:
    schedule.run_pending()
    time.sleep(1)
