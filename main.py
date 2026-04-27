import os
import threading
import time
import requests
import schedule
import asyncio
from flask import Flask
from telegram.ext import Application

# --- CONFIGURATION ---
TOKEN = os.environ.get("BOT_TOKEN")
API_KEY = os.environ.get("FOOTBALL_API_KEY")
CHANNEL_ID = -1003706871581

app = Flask(__name__)
@app.route("/")
def home(): return "Fully Automated Football Bot is Online!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- AUTOMATION LOGIC ---
async def check_and_post_matches(application):
    try:
        # Premier League (PL) မှ ပွဲစဉ်များကို ဆွဲယူခြင်း
        url = "https://api.football-data.org/v4/competitions/PL/matches"
        headers = {"X-Auth-Token": API_KEY}
        response = requests.get(url, headers=headers).json()
        
        matches = response.get('matches', [])
        if not matches:
            print("No matches found.")
            return

        for match in matches:
            status = match.get('status')
            # ပွဲမစရသေးသော ပွဲစဉ်များကိုသာ ကြည့်မည် (TIMED status)
            if status == 'TIMED':
                home_team = match['homeTeam']['name']
                away_team = match['awayTeam']['name']
                
                msg = f"⚽ **UPCOMING MATCH ALERT**\n━━━━━━━━━━━━━━━\n🔴 **{home_team} vs {away_team}**\nဒီနေ့မှာ ယှဉ်ပြိုင်ကစားဖို့ ရှိပါတယ်။\n\n🔗 [တိုက်ရိုက်ကြည့်ရန်လင့်ခ်](https://yallashoot.video/)\n━━━━━━━━━━━━━━━"
                
                await application.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode='Markdown')
                # API Limit ကြောင့် တစ်ကြိမ်လျှင် ပွဲစဉ်အနည်းငယ်သာ စစ်ဆေးမည်
                break 

    except Exception as e:
        print(f"Error checking matches: {e}")

def run_scheduler(application):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # နေ့တိုင်း မြန်မာစံတော်ချိန် နေ့လည် ၁ နာရီခွဲ (UTC 07:00) တွင် အော်တိုစစ်ဆေးရန်
    schedule.every().day.at("07:00").do(lambda: loop.create_task(check_and_post_matches(application)))
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    
    application = Application.builder().token(TOKEN).build()
    
    # Scheduler ကို Background တွင် မောင်းထားခြင်း
    threading.Thread(target=run_scheduler, args=(application,), daemon=True).start()
    
    print("Football Agent Automation is starting...")
    application.run_polling(drop_pending_updates=True) 
