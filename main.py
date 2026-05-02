import time
import threading
import requests
import schedule
from datetime import datetime, timedelta
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

LEAGUES = {
    "🏴 Premier League": "4328",
    "🇪🇸 LaLiga": "4335",
    "🇩🇪 Bundesliga": "4331",
    "🇮🇹 Serie A": "4332",
    "🇫🇷 Ligue 1": "4334",
    "🇪🇺 Champions League": "4480",
}

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CHANNEL_ID, "text": text}, timeout=30)
    print("Telegram:", r.status_code, r.text, flush=True)

def mm_time(date_text, time_text):
    try:
        dt = datetime.fromisoformat(f"{date_text}T{time_text}+00:00")
        dt = dt + timedelta(hours=6, minutes=30)
        return dt.strftime("%d %b %Y | %I:%M %p (MM Time)")
    except:
        return f"{date_text} | {time_text}"

def get_matches(league_id):
    url = "https://www.thesportsdb.com/api/v1/json/1/eventsnextleague.php"
    r = requests.get(url, params={"id": league_id}, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data.get("events") or []

def build_post(match, league_name):
    home = match.get("strHomeTeam", "Home Team")
    away = match.get("strAwayTeam", "Away Team")
    date = match.get("dateEvent", "Unknown Date")
    time_utc = match.get("strTime", "00:00:00")
    venue = match.get("strVenue") or "Venue မသိရသေး"

    title = f"{home} vs {away}"

    text = ""
    text += "🔥 MATCH PREVIEW\n"
    text += "━━━━━━━━━━━━━━\n"
    text += f"⚽ {title}\n"
    text += f"🏆 {league_name}\n"
    text += f"🕒 {mm_time(date, time_utc)}\n"
    text += f"🏟️ {venue}\n\n"

    text += "📊 Match Status\n"
    text += "Upcoming Match\n\n"

    text += "🚑 Injury Update\n"
    text += "Official injury data မရသေးပါ\n\n"

    text += "👥 Expected Lineup\n"
    text += "Official lineup မထွက်သေးပါ\n\n"

    text += "🧠 Match Analysis\n"
    text += "နှစ်သင်းလုံးအတွက် momentum အရေးကြီးပြီး first goal ရတဲ့ဘက်က game control ပိုရနိုင်ပါတယ်။\n\n"

    text += "🎯 Prediction Tip\n"
    text += "Over 1.5 Goals angle = စုစုပေါင်း goal ၂ လုံးနှင့်အထက် ဝင်နိုင်ခြေကို ဆိုလိုပါတယ်။\n\n"

    text += "⚠️ Note: Betting signal မဟုတ်ပါ။ Free data source အခြေခံ preview ဖြစ်ပါတယ်။\n\n"
    text += "#Football #MatchPreview"

    return text

def send_posts():
    print("Building football posts...", flush=True)
    total = 0

    for league_name, league_id in LEAGUES.items():
        try:
            matches = get_matches(league_id)
            print(f"{league_name}: {len(matches)} matches found", flush=True)

            for match in matches[:MATCH_LIMIT]:
                send_message(build_post(match, league_name))
                total += 1
                print("Post sent", flush=True)
                time.sleep(2)

        except Exception as e:
            print(f"{league_name} error: {e}", flush=True)

    if total == 0:
        send_message("⚠️ Upcoming match data မတွေ့သေးပါ။")

    print("Done", flush=True)

if SEND_ON_START:
    send_posts()

schedule.every().day.at(DAILY_POST_TIME).do(send_posts)

print("Football Bot Running...", flush=True)

while True:
    schedule.run_pending()
    time.sleep(1)
