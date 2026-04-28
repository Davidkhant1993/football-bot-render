import os, threading, asyncio, requests
from flask import Flask
from telegram.ext import Application

# --- CONFIGURATION (Token အသစ်ကို အစားထိုးထားသည်) ---
FB_TOKEN = "8498955364:AAHlm0z49sMNxcQUqIaMOnM9evizJUMnl8A"
FOOTBALL_CHANNEL_ID = 1644121104 

app = Flask(__name__)
@app.route("/")
def home(): return "Football Bot is Online!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- ၁။ FOOTBALL NEWS (သတင်းများ) ---
last_fb_news = None

async def fetch_football_news(application):
    global last_fb_news
    print("Football News checker started...")
    while True:
        try:
            # Football News API
            url = "https://newsapi.org/v2/everything?q=football&language=en&pageSize=1&apiKey=62f556947ec548849767858c863f6834"
            response = requests.get(url, timeout=15).json()
            articles = response.get('articles', [])
            
            if articles:
                latest = articles[0]
                if latest['title'] != last_fb_news:
                    last_fb_news = latest['title']
                    title = latest['title']
                    desc = latest['description']
                    link = latest['url']
                    
                    msg = (
                        f"⚽ **FOOTBALL NEWS UPDATES**\n"
                        f"━━━━━━━━━━━━━━━\n"
                        f"📢 {title}\n\n"
                        f"📝 {desc[:150] if desc else ''}...\n\n"
                        f"🔗 [Read More]({link})"
                    )
                    await application.bot.send_message(chat_id=FOOTBALL_CHANNEL_ID, text=msg, parse_mode='Markdown')
            
            await asyncio.sleep(600) 
        except Exception as e:
            await asyncio.sleep(60)

# --- ၂။ LIVE SCORE (ပွဲစဉ်ရလဒ်များ) ---
async def fetch_live_scores(application):
    print("Live Score checker started...")
    while True:
        try:
            url = "https://worldcupjson.net/matches/today" 
            response = requests.get(url, timeout=15).json()
            
            if response:
                for match in response:
                    home = match['home_team']['name']
                    away = match['away_team']['name']
                    status = match['status']
                    
                    if status == "in_progress":
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
    # အသစ်လဲထားသော Token ဖြင့် Application တည်ဆောက်ခြင်း
    application = Application.builder().token(FB_TOKEN).build()
    
    try:
        await application.bot.send_message(
            chat_id=FOOTBALL_CHANNEL_ID, 
            text="⚽ **Football Bot (@MunTalkbot) is now Online!**\n\nသတင်းနဲ့ Live Score များကို စတင်စောင့်ကြည့်နေပါပြီ။"
        )
    except Exception as e:
        print(f"Initial message failed: {e}")

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
