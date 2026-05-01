import time
import asyncio
import threading
import requests
import schedule

from flask import Flask
from telegram import Bot


# =========================================================
# RENDER FREE WEB SERVER
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


# =========================================================
# TELEGRAM SETUP
# =========================================================
bot = Bot(token=BOT_TOKEN)


# =========================================================
# FREE FOOTBALL DATA SOURCE
# =========================================================
def get_matches():
    try:
        url = "https://www.scorebat.com/video-api/v3/"
        response = requests.get(url, timeout=20)
        data = response.json()

        matches = data.get("response", [])

        return matches[:5]

    except Exception as e:
        print(f"Get matches error: {e}", flush=True)
        return []


# =========================================================
# BUILD POST
# =========================================================
def build_post(match):
    title = match.get("title", "Football Match")
    competition = match.get("competition", "Unknown League")
    date = match.get("date", "Unknown Time")

    post = ""
    post += "⚽ MATCH UPDATE\n"
    post += "━━━━━━━━━━━━━━\n\n"

    post += f"🔥 {title}\n\n"
    post += f"🏆 {competition}\n"
    post += f"🕒 {date}\n\n"

    post += "📺 Match Highlights Available\n"
    post += "📊 Live football updates\n"
    post += "🚀 Powered by Football Bot\n\n"

    post += "#Football #LiveFootball"

    return post


# =========================================================
# SEND MESSAGE
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

    matches = get_matches()

    print(f"Matches found: {len(matches)}", flush=True)

    if not matches:
        send_message("❌ No matches found")
        return

    for match in matches:
        try:
            text = build_post(match)

            send_message(text)

            print("Post sent", flush=True)

            time.sleep(2)

        except Exception as e:
            print(f"Send post error: {e}", flush=True)

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
