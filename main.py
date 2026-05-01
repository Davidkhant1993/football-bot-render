import time
import requests
import schedule
from datetime import datetime
from zoneinfo import ZoneInfo
from telegram import Bot


# =========================================================
# 1) EDIT ONLY THESE 3 VALUES
# =========================================================
BOT_TOKEN = "8498955364:AAHlm0z49sMNxcQUqIaMOnM9evizJUMnl8A"
CHANNEL_ID = "@Manchesterunitedfanbased"
API_KEY = "9c873019087d841beb710deb010914b8"


# =========================================================
# 2) BASIC SETTINGS
# =========================================================
TIMEZONE = "Asia/Bangkok"
SEASON = 2025

MATCH_LIMIT_PER_LEAGUE = 3
FORM_MATCH_COUNT = 5
H2H_MATCH_COUNT = 5

DAILY_POST_TIME = "10:00"
SEND_ON_START = True


# =========================================================
# 3) LEAGUE LIST
# =========================================================
LEAGUES = {
    "🏴 Premier League": 39,
    "🇪🇸 LaLiga": 140,
    "🇩🇪 Bundesliga": 78,
    "🇪🇺 Champions League": 2,
    "🏴 Championship": 40,
    "🇮🇹 Serie A": 135,
    "🇫🇷 Ligue 1": 61,
}


# =========================================================
# 4) TELEGRAM + API SETUP
# =========================================================
bot = Bot(token=BOT_TOKEN)

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "v3.football.api-sports.io",
}

BASE_URL = "https://v3.football.api-sports.io"


# =========================================================
# 5) HELPER FUNCTIONS
# =========================================================
def api_get(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}"

    try:
        response = requests.get(url, headers=HEADERS, params=params or {}, timeout=25)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API Error: {endpoint} | {e}")
        return {"response": []}


def format_match_time(date_text):
    try:
        dt = datetime.fromisoformat(date_text.replace("Z", "+00:00"))
        local_dt = dt.astimezone(ZoneInfo(TIMEZONE))
        return local_dt.strftime("%d %b %Y | %I:%M %p")
    except Exception:
        return date_text


def safe_text(value, fallback="မသိရသေး"):
    if value is None or value == "":
        return fallback
    return str(value)


def result_icon(team_id, fixture_item):
    goals_home = fixture_item["goals"]["home"]
    goals_away = fixture_item["goals"]["away"]

    if goals_home is None or goals_away is None:
        return "?"

    home_id = fixture_item["teams"]["home"]["id"]
    away_id = fixture_item["teams"]["away"]["id"]

    if goals_home == goals_away:
        return "➖"

    home_win = goals_home > goals_away

    if team_id == home_id:
        return "✅" if home_win else "❌"

    if team_id == away_id:
        return "❌" if home_win else "✅"

    return "?"


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
        return "Form data မတွေ့သေးပါ"

    icons = [result_icon(team_id, item) for item in fixtures]
    return "".join(icons)


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
        return "H2H data မတွေ့သေးပါ"

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
            elif item_home_id == away_id:
                away_wins += 1
        else:
            if item_away_id == home_id:
                home_wins += 1
            elif item_away_id == away_id:
                away_wins += 1

    return f"Home win {home_wins} | Draw {draws} | Away win {away_wins}"


def get_injuries(team_id, fixture_id=None):
    params = {"team": team_id, "season": SEASON}
    if fixture_id:
        params["fixture"] = fixture_id

    data = api_get("injuries", params)
    injuries = data.get("response", [])

    if not injuries:
        return []

    players = []
    for item in injuries[:5]:
        player_name = safe_text(item.get("player", {}).get("name"), "Unknown player")
        reason = safe_text(item.get("player", {}).get("reason"), "Injury")
        players.append(f"{player_name} ({reason})")

    return players


def build_simple_prediction(home_name, away_name, home_form, away_form):
    home_score = home_form.count("✅") - home_form.count("❌")
    away_score = away_form.count("✅") - away_form.count("❌")

    if home_score > away_score + 1:
        analysis = f"{home_name} ဘက်က recent form အရ နည်းနည်းအသာရနေတယ်။"
        tip = f"{home_name} မရှုံးနိုင်ခြေ / Win or Draw angle"
    elif away_score > home_score + 1:
        analysis = f"{away_name} ဘက်က recent form အရ ပိုသန်မာနေတယ်။"
        tip = f"{away_name} မရှုံးနိုင်ခြေ / Win or Draw angle"
    else:
        analysis = "Form ပိုင်းက သိပ်မကွာလို့ balanced game ဖြစ်နိုင်တယ်။"
        tip = "Draw chance ထည့်စဉ်းစားလို့ရတဲ့ပွဲ"

    return analysis, tip


# =========================================================
# 6) BUILD MATCH PREVIEW
# =========================================================
def build_match_preview(match, league_name):
    fixture = match["fixture"]
    teams = match["teams"]

    fixture_id = fixture["id"]
    venue = safe_text(fixture.get("venue", {}).get("name"), "Venue မသိရသေး")
    match_time = format_match_time(fixture["date"])

    home = teams["home"]
    away = teams["away"]

    home_id = home["id"]
    away_id = away["id"]
    home_name = home["name"]
    away_name = away["name"]

    home_form = team_form(home_id, match["league"]["id"])
    away_form = team_form(away_id, match["league"]["id"])
    h2h_text = h2h_summary(home_id, away_id)

    home_injuries = get_injuries(home_id, fixture_id)
    away_injuries = get_injuries(away_id, fixture_id)

    analysis, tip = build_simple_prediction(home_name, away_name, home_form, away_form)

    text = ""
    text += f"🔥 Match Preview — {home_name} vs {away_name}\n"
    text += "━━━━━━━━━━━━━━\n"
    text += f"🏆 {league_name}\n"
    text += f"🕒 {match_time}\n"
    text += f"🏟️ {venue}\n\n"

    text += "📊 Recent Form\n"
    text += f"{home_name}: {home_form}\n"
    text += f"{away_name}: {away_form}\n\n"

    text += "📈 H2H\n"
    text += f"Last {H2H_MATCH_COUNT} meetings: {h2h_text}\n\n"

    text += "🚑 Injury / Missing Players\n"
    if home_injuries:
        text += f"❌ {home_name}: " + ", ".join(home_injuries) + "\n"
    else:
        text += f"✅ {home_name}: major injury data မတွေ့သေးပါ\n"

    if away_injuries:
        text += f"❌ {away_name}: " + ", ".join(away_injuries) + "\n"
    else:
        text += f"✅ {away_name}: major injury data မတွေ့သေးပါ\n"

    text += "\n🧠 Analysis\n"
    text += analysis
    text += " H2H နဲ့ injury data ကိုပါကြည့်ရင် ပွဲက momentum ပေါ်မူတည်နိုင်ပါတယ်။\n\n"

    text += "🎯 Prediction Tip\n"
    text += tip + "\n\n"

    text += "⚠️ Note: Betting signal မဟုတ်ပါ။ Form, H2H, injury data အခြေခံပြီး football analysis အနေနဲ့ သုံးသပ်ထားတာပါ။\n"

    return text


# =========================================================
# 7) GET UPCOMING MATCHES
# =========================================================
def get_upcoming_fixtures(league_id):
    data = api_get(
        "fixtures",
        {
            "league": league_id,
            "season": SEASON,
            "next": MATCH_LIMIT_PER_LEAGUE,
        },
    )
    return data.get("response", [])


def build_full_post():
    text = "⚽ ဒီတစ်ပတ် လူကြည့်များမယ့် ပွဲစဉ် Preview များ\n"
    text += "━━━━━━━━━━━━━━\n\n"

    for league_name, league_id in LEAGUES.items():
        matches = get_upcoming_fixtures(league_id)

        if not matches:
            text += f"{league_name}\n"
            text += "⚠️ Upcoming match data မတွေ့သေးပါ\n\n"
            continue

        for match in matches:
            try:
                text += build_match_preview(match, league_name)
                text += "\n\n"
                time.sleep(1)
            except Exception as e:
                print(f"Build preview error: {league_name} | {e}")
                text += f"⚠️ {league_name} preview တစ်ခု build မလုပ်နိုင်ပါ\n\n"

    text += "#Football #MatchPreview #FootballNews"
    return text


# =========================================================
# 8) TELEGRAM SEND
# =========================================================
def send_long_message(chat_id, text):
    max_len = 3900

    if len(text) <= max_len:
        bot.send_message(chat_id=chat_id, text=text)
        return

    parts = []
    current = ""

    for block in text.split("\n\n"):
        if len(current) + len(block) + 2 <= max_len:
            current += block + "\n\n"
        else:
            parts.append(current)
            current = block + "\n\n"

    if current:
        parts.append(current)

    for part in parts:
        bot.send_message(chat_id=chat_id, text=part)
        time.sleep(1)


def send_football_posts():
    print("Building football post...")
    text = build_full_post()
    send_long_message(CHANNEL_ID, text)
    print("✅ Football post sent to Telegram")


# =========================================================
# 9) RUN
# =========================================================
if SEND_ON_START:
    send_football_posts()

schedule.every().day.at(DAILY_POST_TIME).do(send_football_posts)

print("⚽ Football Telegram Bot Running...")
print(f"Daily post time: {DAILY_POST_TIME}")

while True:
    schedule.run_pending()
    time.sleep(1)
