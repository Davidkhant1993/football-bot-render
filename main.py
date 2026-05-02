import time
import threading
import requests
import schedule
from datetime import datetime, timedelta
from flask import Flask


# =========================================================
# FLASK WEB SERVER FOR RENDER
# =========================================================
app = Flask(__name__)

@app.route("/")
def home():
    return "Football Bot Running"


def run_web():
    app.run(host="0.0.0.0", port=10000)


threading.Thread(target=run_web).start()


# =========================================================
# TELEGRAM SETTINGS
# =========================================================
BOT_TOKEN = "8498955364:AAHlm0z49sMNxcQUqIaMOnM9evizJUMnl8A"
CHANNEL_ID = "@Manchesterunitedfanbased"

SEND_ON_START = True
DAILY_POST_TIME = "10:00"
MATCH_LIMIT = 5


# =========================================================
# TELEGRAM SEND
# =========================================================
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        response = requests.post(
            url,
            data={
                "chat_id": CHANNEL_ID,
                "text": text
            },
            timeout=30
        )

        print("Telegram status:", response.status_code, flush=True)
        print("Telegram response:", response.text, flush=True)

    except Exception as e:
        print(f"Telegram send error: {e}", flush=True)


# =========================================================
# MYANMAR TIME FORMAT
# =========================================================
def mm_time(date_text, time_text):
    try:
        dt = datetime.fromisoformat(f"{date_text}T{time_text}+00:00")
        dt = dt + timedelta(hours=6, minutes=30)
        return dt.strftime("%d %b %Y | %I:%M %p (MM Time)")
    except Exception:
        return f"{date_text} | {time_text}"


# =========================================================
# FREE MATCH SOURCE + FALLBACK
# =========================================================
def get_matches(league_id):
    try:
        url = "https://www.thesportsdb.com/api/v1/json/1/eventsnextleague.php"

        response = requests.get(
            url,
            params={"id": league_id},
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        matches = data.get("events")

        if matches:
            return matches[:MATCH_LIMIT]

    except Exception as e:
        print(f"SportsDB error: {e}", flush=True)

    return [
        {
            "strHomeTeam": "Manchester City",
            "strAwayTeam": "Arsenal",
            "dateEvent": "2026-05-02",
            "strTime": "19:00:00",
            "strVenue": "Etihad Stadium",
        },
        {
            "strHomeTeam": "Barcelona",
            "strAwayTeam": "Real Madrid",
            "dateEvent": "2026-05-02",
            "strTime": "20:00:00",
            "strVenue": "Camp Nou",
        },
        {
            "strHomeTeam": "Bayern Munich",
            "strAwayTeam": "Dortmund",
            "dateEvent": "2026-05-02",
            "strTime": "18:30:00",
            "strVenue": "Allianz Arena",
        },
    ]


# =========================================================
# LEAGUES
# =========================================================
LEAGUES = {
    "🏴 Premier League": "4328",
    "🇪🇸 LaLiga": "4335",
    "🇩🇪 Bundesliga": "4331",
}


# =========================================================
# ANALYSIS
# =========================================================
def build_analysis(home, away):
    teams = f"{home} {away}".lower()

    if "manchester" in teams or "arsenal" in teams:
        return (
            "ဒီပွဲမှာ attacking transition နဲ့ midfield control "
            "က အရေးကြီးနိုင်ပြီး first goal ရတဲ့ဘက်က momentum ပိုရနိုင်ပါတယ်။"
        )

    if "barcelona" in teams or "real madrid" in teams:
        return (
            "El Clasico type big match ဖြစ်နိုင်ပြီး possession control "
            "နဲ့ counter attack timing က result ကိုဆုံးဖြတ်နိုင်ပါတယ်။"
        )

    if "bayern" in teams or "dortmund" in teams:
        return (
            "Bundesliga big match ဖြစ်နိုင်ပြီး high pressing နဲ့ pace transition "
            "တွေက ပွဲကိုအဆုံးအဖြတ်ပေးနိုင်ပါတယ်။"
        )

    return (
        "နှစ်သင်းလုံးအတွက် momentum အရေးကြီးပြီး "
        "defensive concentration က result ကိုသတ်မှတ်နိုင်ပါတယ်။"
    )


def build_tip(home, away):
    teams = f"{home} {away}".lower()

    if "barcelona" in teams or "real madrid" in teams:
        return "BTTS / Over 1.5 Goals angle စဉ်းစားလို့ရပါတယ်။"

    return "Over 1.5 Goals angle စဉ်းစားလို့ရပါတယ်။"


# =========================================================
# BUILD POST
# =========================================================
def build_post(match, league_name):
    home = match.get("strHomeTeam", "Home Team")
    away = match.get("strAwayTeam", "Away Team")
    date = match.get("dateEvent", "Unknown Date")
    time_utc = match.get("strTime", "00:00:00")
    venue = match.get("strVenue") or "Venue မသိရသေး"

    text = ""
    text += "🔥 MATCH PREVIEW\n"
    text += "━━━━━━━━━━━━━━\n"
    text += f"⚽ {home} vs {away}\n"
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
    text += build_analysis(home, away) + "\n\n"

    text += "🎯 Prediction Tip\n"
    text += build_tip(home, away) + "\n\n"

    text += "⚠️ Note: Betting signal မဟုတ်ပါ။ Free data source / fallback preview ဖြစ်ပါတယ်။\n\n"
    text += "#Football #MatchPreview"

    return text


# =========================================================
# SEND POSTS
# =========================================================
def send_posts():
    print("Building football posts...", flush=True)

    total = 0

    for league_name, league_id in LEAGUES.items():
        matches = get_matches(league_id)

        print(f"{league_name}: {len(matches)} matches found", flush=True)

        for match in matches[:MATCH_LIMIT]:
            send_message(build_post(match, league_name))
            total += 1
            print("Post sent", flush=True)
            time.sleep(2)

    if total == 0:
        send_message("⚠️ Upcoming match data မတွေ့သေးပါ။")

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
