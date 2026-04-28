import os, threading, asyncio, requests
from flask import Flask
from telegram.ext import Application

# --- CONFIGURATION ---
FB_TOKEN = "7953760451:AAFl-H5Ym7vC-XqE22_3_ZJ56zN5G0Gv-9w"
FOOTBALL_CHANNEL_ID = 1644121104  # လူကြီးမင်းရဲ့ Channel ID သို့မဟုတ် Chat ID
# Football Data API Key (အကယ်၍ ရှိလျှင် ဤနေရာတွင် ထည့်ပါ၊ မရှိလျှင် Free API သုံးပါမည်)
FB_API_KEY = "YOUR_FOOTBALL_DATA_API_KEY" 

app = Flask(__name__)
@app.route("/")
def home(): return "Football Bot is Online!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10001)) # Crypto Bot နဲ့ မတူအောင် Port ပြောင်းထားသည်
    app.run(host="0.0.0.0", port=port)

# --- ၁။ FOOTBALL LIVE UPDATES ---
async def fetch_football_matches(application):
    print("Football checker started...")
    while True:
        try:
            # Free API တစ်ခုဖြစ်သော LiveScore API သို့မဟုတ် အခြား Source တစ်ခုခုမှ ဒေတာယူခြင်း
            url = "https://worldcupjson.net/matches/today" # ဥပမာ API တစ်ခု
            response = requests.get(url, timeout=15).json()
            
            if response:
                for match in response:
                    home_team = match['home_team']['name']
                    away_team = match['away_team']['name']
                    status = match['status']
                    
                    if status == "in_progress":
                        score = f"{match['home_team']['goals']} - {match['away_team']['goals']}"
                        msg = (
                            f"⚽ **LIVE MATCH UPDATE**\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"🏟 {home_team} vs {away_team}\n"
                            f"🔢 Score: {score}\n"
                            f"⏱ Status: Live Now"
                        )
                        await application.bot.send_message(chat_id=FOOTBALL_CHANNEL_ID, text=msg)
            
            await asyncio.sleep(300) # ၅ မိနစ်တစ်ခါ စစ်မည်
        except Exception as e:
            print(f"Football System Error: {e}")
            await asyncio.sleep(60)

async def start_fb_bot():
    application = Application.builder().token(FB_TOKEN).build()
    
    # Bot တက်လာကြောင်း အသိပေးစာ (Crypto Bot လိုမျိုး စမ်းသပ်ရန်)
    try:
        await application.bot.send_message(
            chat_id=FOOTBALL_CHANNEL_ID, 
            text="⚽ **Football Bot Active!**\n\nဒီနေ့ပွဲစဉ်တွေနဲ့ Live Score တွေကို ဒီမှာ တင်ပေးသွားမှာပါဗျ။"
        )
    except: pass

    async with application:
        await application.initialize()
        await application.start()
        
        asyncio.create_task(fetch_football_matches(application))
        await asyncio.Event().wait()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    try:
        asyncio.run(start_fb_bot())
    except KeyboardInterrupt:
        pass 
