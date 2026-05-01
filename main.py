import time
import asyncio
import threading
import requests
import schedule
from datetime import datetime
from zoneinfo import ZoneInfo
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
# EDIT ONLY THESE 3 VALUES
# =========================================================
BOT_TOKEN = "8498955364:AAHlm0z49sMNxcQUqIaMOnM9evizJUMnl8A"
CHANNEL_ID = "@Manchesterunitedfanbased"
FOOTBALL_DATA_API_KEY = "05185bb3dbcc47589a2fa06c6172d268"


# =========================================================
# SETTINGS
# =========================================================
TIMEZONE = "Asia/Bangkok"
SEND_ON_START = True
DAILY_POST_TIME = "10:00"
MATCH_LIMIT = 5


# =========================================================
# API SETUP
# =========================================================
bot = Bot(token=BOT_TOKEN)

BASE_URL = "https://api.football-data.org/v4"

HEADERS = {
    "X-Auth-Token": FOOTBALL_DATA_API_KEY
}


# =========================================================
# LEAGUES
# =========================================================
COMPETITIONS = {
    "🏴 Premier League": "PL",
    "🇪🇸 LaLiga": "PD",
    "🇩🇪 Bundesliga": "BL1",
    "🇮🇹 Serie A": "SA",
    "🇫🇷 Ligue 1": "FL1",
    "🇪🇺 Champions League": "CL",
}


# =========================================================
# API REQUEST
# =========================================================
def api_get(endpoint, params=None):
    try:
        url = f"{BASE_URL}/{endpoint}"

        response = requests.get(
            url,
            headers=HEADERS,
            params=params or {},
            timeout=60
        )

        print(f"API {endpoint}: {response.status_code}", flush=True)

        response.raise_for_status()
        return response.json()

    except Exception as e:
        print(f"API Error: {endpoint} | {e}", flush=True)
        return {}


# =========================================================
# TIME FORMAT
# =========================================================
def format_time(utc_date):
    try:
        dt = datetime.fromisoformat(utc_date.replace("Z", "+00:00"))
        local_dt = dt.astimezone(ZoneInfo(TIMEZONE))
        return local_dt.strftime("%d %b %Y | %I:%M %p")
    except Exception:
        return utc_date


# =========================================================
# GET UPCOMING MATCHES
# =========================================================
def get_matches(competition_code):
    data = api_get(
        f"competitions/{competition_code}/matches",
        {
            "status": "SCHEDULED"
        }
    )

    matches = data.get("matches", [])
    return matches[:MATCH_LIMIT]


# =========================================================
# GET STANDINGS
# =========================================================
def get_standings(competition_code):
    data = api_get(f"competitions/{competition_code}/standings")

    standings = {}

    tables = data.get("standings", [])

    if not tables:
        return standings

    table = tables[0].get("table", [])

    for item in table:
        team_name = item.get("team", {}).get("name")
        position = item.get("position")
        points = item.get("points")
        form = item.get("form", "N/A")

        if team_name:
            standings[team_name] = {
                "position": position,
                "points": points,
                "form": form
            }

    return standings


# =========================================================
# SIMPLE ANALYSIS
# =========================================================
def build_prediction(home_info, away_info):
    home_points = home_info.get("points", 0) if home_info else 0
    away_points = away_info.get("points", 0) if away_info else 0

    if home_points > away_points + 5:
        return "Home team ဘက်က league standing အရ အသာရနိုင်ပါတယ်။"
    elif away_points > home_points + 5:
        return "Away team ဘက်က league standing အရ အသာရနိုင်ပါတယ်။"
    else:
        return "နှစ်သင်း rating မကွာလို့ balanced game ဖြစ်နိုင်ပါတယ်။"


def build_tip(home_info, away_info):
    home_points = home_info.get("points", 0) if home_info else 0
    away_points = away_info.get("points", 0) if away_info else 0

    if abs(home_points - away_points) <= 5:
        return "Draw chance / Over 1.5 Goals angle စဉ်းစားလို့ရပါတယ်။"
    elif home_points > away_points:
        return "Home team မရှုံးနိုင်ခြေ angle စဉ်းစားလို့ရပါတယ်။"
    else:
        return "Away team မရှုံးနိုင်ခြေ angle စဉ်းစားလို့ရပါတယ်။"


# =========================================================
# BUILD POST
# =========================================================
def build_post(match, league_name, standings):
    home = match.get("homeTeam", {}).get("name", "Home Team")
    away = match.get("awayTeam", {}).get("name", "Away Team")
    utc_date = match.get("utcDate", "Unknown Time")
    match_time = format_time(utc_date)

    home_info = standings.get(home, {})
    away_info = standings.get(away, {})

    home_pos = home_info.get("position", "N/A")
    away_pos = away_info.get("position", "N/A")

    home_points = home_info.get("points", "N/A")
    away_points = away_info.get("points", "N/A")

    home_form = home_info.get("form", "Data မရသေးပါ")
    away_form = away_info.get("form", "Data မရသေးပါ")

    analysis = build_prediction(home_info, away_info)
    tip = build_tip(home_info, away_info)

    text = ""
    text += "🔥 MATCH PREVIEW\n"
    text += "━━━━━━━━━━━━━━\n"
    text += f"⚽ {home} vs {away}\n"
    text += f"🏆 {league_name}\n"
    text += f"🕒 {match_time}\n\n"

    text += "📊 League Position\n"
    text += f"{home}: #{home_pos} | {home_points} pts\n"
    text += f"{away}: #{away_pos} | {away_points} pts\n\n"

    text += "📈 Recent Form\n"
    text += f"{home}: {home_form}\n"
    text += f"{away}: {away_form}\n\n"

    text += "🚑 Injury Update\n"
    text += "Free API မှာ official injury data မပါသေးပါ\n\n"

    text += "👥 Expected Lineup\n"
    text += "Lineup မထွက်သေးပါ / Free API မှာ lineup data မပါသေးပါ\n\n"

    text += "🧠 Match Analysis\n"
    text += analysis + "\n\n"

    text += "🎯 Prediction Tip\n"
    text += tip + "\n\n"

    text += "⚠️ Note: Betting signal မဟုတ်ပါ။ Free football-data.org data အခြေခံပြီး preview ရေးထားတာပါ။\n\n"

    text += "#Football #MatchPreview"

    return text


# =========================================================
# SEND TELEGRAM
# =========================================================
def send_message(text):
    asyncio.run(
        bot.send_message(
            chat_id=CHANNEL_ID,
            text=text
        )
    )


# =========================================================
# SEND POSTS
# =========================================================
def send_posts():
    print("Building football posts...", flush=True)

    total_posts = 0

    for league_name, competition_code in COMPETITIONS.items():
        print(f"Checking {league_name}", flush=True)

        matches = get_matches(competition_code)
        print(f"{league_name}: {len(matches)} matches found", flush=True)

        if not matches:
            continue

        standings = get_standings(competition_code)

        for match in matches:
            try:
                text = build_post(match, league_name, standings)
                send_message(text)

                total_posts += 1
                print("Post sent", flush=True)

                time.sleep(2)

            except Exception as e:
                print(f"Send error: {e}", flush=True)

    if total_posts == 0:
        send_message("⚠️ ဒီနေ့ upcoming match data မတွေ့သေးပါ။")

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
