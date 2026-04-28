import os, threading, asyncio, requests, xml.etree.ElementTree as ET
from flask import Flask
from telegram.ext import Application

# --- CONFIGURATION ---
FB_TOKEN = "8498955364:AAHlm0z49sMNxcQUqIaMOnM9evizJUMnl8A"
FOOTBALL_CHANNEL_ID = 1644121104 

app = Flask(__name__)
@app.route("/")
def home(): return "Football Bot is Online!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- ၁။ GOOGLE NEWS FEED (ပိုမြန်၊ ပိုစုံသော သတင်းစနစ်) ---
last_fb_link = None

async def fetch_football_news(application):
    global last_fb_link
    print("Football News checker started via Google Feed...")
    while True:
        try:
            # Google News RSS Feed (Football)
            url = "https://news.google.com/rss/search?q=football+news&hl=en-US&gl=US&ceid=US:en"
            response = requests.get(url, timeout=15)
            root = ET.fromstring(response.content)
            
            # နောက်ဆုံးတက်လာတဲ့ သတင်းကို ယူခြင်း
            item = root.find('.//item')
            if item is not None:
                title = item.find('title').text
                link = item.find('link').text
                
                if link != last_fb_link:
                    last_fb_link = link
                    msg = (
                        f"⚽ **LATEST FOOTBALL NEWS**\n"
                        f"━━━━━━━━━━━━━━━\n"
                        f"📢 {title}\n\n"
                        f"🔗 [သတင်းအပြည့်အစုံဖတ်ရန်]({link})"
                    )
                    await application.bot.send_message(chat_id=FOOTBALL_CHANNEL_ID, text=msg, parse_mode='Markdown')
            
            await asyncio.sleep(300) # ၅ မိနစ်တစ်ခါ စစ်မည်
        except Exception as e:
            print(f"News Feed Error: {e}")
            await asyncio.sleep(60)

# --- ၂။ LIVE SCORE စနစ် ---
async def fetch_live_scores(application):
    print("Live Score checker started...")
    while True:
        try:
            url = "https://worldcupjson.net/matches/today" 
            response = requests.get(url, timeout=15).json()
            if response:
                for match in response:
                    if match['status'] == "in_progress":
                        home = match['home_team']['name']
                        away = match['away_team']['name']
                        score = f"{match['home_team']['goals']} - {match['away_team']['goals']}"
                        msg = (
                            f"⚽ **LIVE MATCH UPDATE**\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"🏟 {home} vs {away}\n"
                            f"🔢 Score: {score}\n"
                            f"⏱ Status: Live Now"
                        )
                        await application.bot.send_message(chat_id=FOOTBALL_CHANNEL_ID, text=msg)
            await asyncio.sleep(300)
        except Exception:
            await asyncio.sleep(60)

async def start_fb_bot():
    application = Application.builder().token(FB_TOKEN).build()
    
    # Bot စတက်တာနဲ့ စာတစ်စောင် အရင်ပို့ခိုင်းပါမယ် (Connection စစ်ရန်)
    try:
        await application.bot.send_message(
            chat_id=FOOTBALL_CHANNEL_ID, 
            text="⚽ **Football System Updated!**\n\nGoogle News Feed နဲ့ ချိတ်ဆက်လိုက်ပါပြီ။ သတင်းအသစ်တွေ ချက်ချင်းတက်လာပါလိမ့်မယ်ဗျ။"
        )
    except: pass

    async with application:
        await application.initialize()
        await application.start()
        asyncio.create_task(fetch_football_news(application))
        asyncio.create_task(fetch_live_scores(application))
        await asyncio.Event().wait()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    try:
        asyncio.run(start_fb_bot())
    except KeyboardInterrupt:
        pass 
