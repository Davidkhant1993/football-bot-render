import time
import threading
import requests
import schedule
from datetime import datetime, timedelta, timezone
from flask import Flask


app = Flask(__name__)

@app.route("/")
def home():
    return "Football Bot Running"


def run_web():
    app.run(host="0.0.0.0", port=10000)


threading.Thread(target=run_web).start()


BOT_TOKEN = "8498955364:AAHlm0z49sMNxcQUqIaMOnM9evizJUMnl8A"
CHANNEL_ID = "@Manchesterunitedfanbased"

SEND_ON_START = True
DAILY_POST_TIME = "10:00"
MATCH_LIMIT = 5


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(
        url,
        data={
            "chat_id": CHANNEL_ID,
            "text": text
        },
        timeout=30
    )


def format_time(date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        mm_time = dt + timedelta(hours=6, minutes=30)
        return mm_time.strftime("%d %b %Y | %I:%M %p (MM Time)")
    except:
        return date_str


def get_matches():
    try:
        url = "https://www.scorebat.com/video-api/v3/"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        matches = data.get("response", [])
        final_matches = []
        now = datetime.now(timezone.utc)

        for match in matches:
            title = match.get("title", "Football Match")
            competition = match.get("competition", "Football")
            date = match.get("date", "")

            try:
                match_time = datetime.fromisoformat(date.replace("Z", "+00:00"))
            except:
                continue

            if match_time <= now:
                continue

            final_matches.append({
                "title": title,
                "competition": competition,
                "date": date
            })

        return final_matches[:MATCH_LIMIT]

    except Exception as e:
        print(f"Get matches error: {e}", flush=True)
        return []


def clean_competition(comp):
    if isinstance(comp, dict):
        return comp.get("name", "Football")
    return str(comp)


def build_post(match):
    title = match.get("title", "Football Match")
    competition = clean_competition(match.get("competition", "Football"))
    date = format_time(match.get("date", "Unknown Time"))

    text = ""
    text += "🔥 MATCH PREVIEW\n"
    text += "━━━━━━━━━━━━━━\n"
    text += f"⚽ {title}\n"
    text += f"🏆 {competition}\n"
    text += f"🕒 {date}\n\n"

    text += "📊 Match Status\n"
    text += "Upcoming Match\n\n"

    text += "🚑 Injury Update\n"
    text += "Official injury data မရသေးပါ\n\n"

    text += "👥 Expected Lineup\n"
    text += "Official lineup မထွက်သေးပါ\n\n"

    text += "🧠 Match Analysis\n"
    text += "နှစ်သင်းလုံးအတွက် momentum အရေးကြီးပြီး first goal ရတဲ့ဘက်က game control ပိုရနိုင်ပါတယ်။\n\n"

    text += "🎯 Prediction Tip\n"
    text += "Over 1.5 Goals angle စဉ်းစားလို့ရပါတယ်။\n\n"

    text += "⚠️ Note: Betting signal မဟုတ်ပါ။ Free source အခြေခံ preview ဖြစ်ပါတယ်။\n\n"
    text += "#Football #MatchPreview"

    return text


def send_posts():
    print("Building football posts...", flush=True)

    matches = get_matches()
    print(f"Upcoming matches found: {len(matches)}", flush=True)

    if not matches:
        send_message("⚠️ Upcoming match data မတွေ့သေးပါ။ ပွဲအဟောင်းတွေကို မပို့အောင် filter လုပ်ထားပါတယ်။")
        return

    for match in matches:
        send_message(build_post(match))
        print("Post sent", flush=True)
        time.sleep(2)

    print("Done", flush=True)


if SEND_ON_START:
    send_posts()

schedule.every().day.at(DAILY_POST_TIME).do(send_posts)

print("Football Bot Running...", flush=True)

while True:
    schedule.run_pending()
    time.sleep(1)
