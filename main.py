import time
import requests
import schedule
import asyncio
import threading

from flask import Flask
from datetime import datetime
from zoneinfo import ZoneInfo
from telegram import Bot


# =========================================================
# FLASK WEB SERVER FOR RENDER FREE PLAN
# =========================================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Football Bot Running"


def run_web():
    app.run(host="0.0.0.0", port=10000)


threading.Thread(target=run_web).start()


# =========================================================
# EDIT THESE 3 VALUES
# =========================================================
BOT_TOKEN = "8498955364:AAHlm0z49sMNxcQUqIaMOnM9evizJUMnl8A"
CHANNEL_ID = "@Manchesterunitedfanbased"
API_KEY = "9c873019087d841beb710deb010914b8"


# =========================================================
# BASIC SETTINGS
# =========================================================
TIMEZONE = "Asia/Bangkok"
SEASON = 2026

MATCH_LIMIT_PER_LEAGUE = 2
FORM_MATCH_COUNT = 5
H2H_MATCH_COUNT = 5

DAILY_POST_TIME = "10:00"
SEND_ON_START = True


# =========================================================
# LEAGUES
# =========================================================
LEAGUES = {
    "🏴 Premier League": 39,
    "🇪🇸 LaLiga": 140,
    "🇩🇪 Bundesliga": 78,
    "🇪🇺 Champions League": 2,
}


# =========================================================
# TELEGRAM + API
# =========================================================
bot = Bot(token=BOT_TOKEN)

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "v3.football.api-sports.io",
}

BASE_URL = "https://v3.football.api-sports.io"


# =========================================================
# API REQUEST
# =========================================================
def api_get(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}"

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            params=params or {},
            timeout=25
        )

        response.raise_for_status()
        return response.json()

    except Exception as e:
        print(f"API Error: {endpoint} | {e}")
        return {"response": []}


# =========================================================
# TIME FORMAT
# =========================================================
def format_match_time(date_text):
    try:
        dt = datetime.fromisoformat(date_text.replace("Z", "+00:00"))
        local_dt = dt.astimezone(ZoneInfo(TIMEZONE))

        return local_dt.strftime("%d %b %Y | %I:%M %p")

    except Exception:
        return date_text


# =========================================================
# TEAM FORM
# =========================================================
def result_icon(team_id, fixture_item):
    goals_home = fixture_item["goals"]["home"]
    goals_away = fixture_item["goals"]["away"]

    if goals_home is None or goals_away is None:
        return "➖"

    home_id = fixture_item["teams"]["home"]["id"]
    away_id = fixture_item["teams"]["away"]["id"]

    if goals_home == goals_away:
        return "➖"

    home_win = goals_home > goals_away

    if team_id == home_id:
        return "✅" if home_win else "❌"

    if team_id == away_id:
        return "❌" if home_win else "✅"

    return "➖"


def team_form(team_id, league_id):
    data = api_get(
        "fixtures",
        {
            "team": team_id,
            "league": league_id,
            "season": SEASON,
            "last": FORM_MATCH_COUNT,
        },
    )

    fixtures = data.get("response", [])

    if not fixtures:
        return "No form data"

    icons = [result_icon(team_id, item) for item in fixtures]

    return "".join(icons)


# =========================================================
# H2H
# =========================================================
def h2h_summary(home_id, away_id):
    data = api_get(
        "fixtures/headtohead",
        {
            "h2h": f"{home_id}-{away_id}",
            "last": H2H_MATCH_COUNT,
        },
    )

    fixtures = data.get("response", [])

    if not fixtures:
        return "No H2H data"

    home_wins = 0
    away_wins = 0
    draws = 0

    for item in fixtures:
        goals_home = item["goals"]["home"]
        goals_away = item["goals"]["away"]

        if goals_home is None or goals_away is None:
            continue

        item_home_id = item["teams"]["home"]["id"]
        item_away_id = item["teams"]["away"]["id"]

        if goals_home == goals_away:
            draws += 1

        elif goals_home > goals_away:
            if item_home_id == home_id:
                home_wins += 1
            else:
                away_wins += 1

        else:
            if item_away_id == home_id:
                home_wins += 1
            else:
                away_wins += 1

    return f"{home_wins}W - {draws}D - {away_wins}W"


# =========================================================
# INJURY
# =========================================================
def get_injuries(team_id):
    data = api_get(
        "injuries",
        {
            "team": team_id,
            "season": SEASON,
        },
    )

    injuries = data.get("response", [])

    if not injuries:
        return []

    players = []

    for item in injuries[:3]:
        player = item.get("player", {}).get("name", "Unknown")
        players.append(player)

    return players


# =========================================================
# BUILD PREVIEW
# =========================================================
def build_match_preview(match, league_name):
    fixture = match["fixture"]
    teams = match["teams"]

    home = teams["home"]
    away = teams["away"]

    home_id = home["id"]
    away_id = away["id"]

    home_name = home["name"]
    away_name = away["name"]

    match_time = format_match_time(fixture["date"])

    home_form = team_form(home_id, match["league"]["id"])
    away_form = team_form(away_id, match["league"]["id"])

    h2h = h2h_summary(home_id, away_id)

    home_injuries = get_injuries(home_id)
    away_injuries = get_injuries(away_id)

    text = ""
    text += f"🔥 {home_name} vs {away_name}\n"
    text += "━━━━━━━━━━━━━━\n"
    text += f"🏆 {league_name}\n"
    text += f"🕒 {match_time}\n\n"

    text += "📊 Recent Form\n"
    text += f"{home_name}: {home_form}\n"
    text += f"{away_name}: {away_form}\n\n"

    text += "📈 H2H\n"
    text += f"{h2h}\n\n"

    text += "🚑 Injuries\n"

    if home_injuries:
        text += f"{home_name}: {', '.join(home_injuries)}\n"
    else:
        text += f"{home_name}: No major injuries\n"

    if away_injuries:
        text += f"{away_name}: {', '.join(away_injuries)}\n"
    else:
        text += f"{away_name}: No major injuries\n"

    text += "\n#Football #MatchPreview"

    return text


# =========================================================
# UPCOMING FIXTURES
# =========================================================
def get_upcoming_matches(league_id):
    data = api_get(
        "fixtures",
        {
            "league": league_id,
            "season": SEASON,
            "next": MATCH_LIMIT_PER_LEAGUE,
        },
    )

    return data.get("response", [])


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


def send_posts():
    print("Building football posts...")

    for league_name, league_id in LEAGUES.items():
        matches = get_upcoming_matches(league_id)
        print(f"{league_name}: {len(matches)} matches found")

        if not matches:
            continue

        for match in matches:
            try:
                text = build_match_preview(match, league_name)

                send_message(text)

                print("Post sent")

                time.sleep(2)

            except Exception as e:
                print(f"Error: {e}")

    print("Done")


# =========================================================
# RUN
# =========================================================
if SEND_ON_START:
    send_message("✅ Bot test post is working")
    send_posts()

schedule.every().day.at(DAILY_POST_TIME).do(send_posts)

print("Football Bot Running...")


while True:
    schedule.run_pending()
    time.sleep(1)
