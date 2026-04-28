import os, threading, asyncio, requests, xml.etree.ElementTree as ET
from flask import Flask
from telegram.ext import Application

# --- CONFIGURATION (ID အမှန်ကို အစားထိုးထားသည်) ---
FB_TOKEN = "8498955364:AAHlm0z49sMNxcQUqIaMOnM9evizJUMnl8A"
FOOTBALL_CHANNEL_ID = -1003706871581 

app = Flask(__name__)
@app.route("/")
def home(): return "Football Bot is Online!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- ၁။ GOOGLE NEWS FEED ---
last_fb_link = None

async def fetch_football_news(application):
    global last_fb_link
    print("Football News checker started...")
    while True:
        try:
            url = "https://news.google.com/rss/search?q=football+news&hl=en-US&gl=US&ceid=US:en"
            response = requests.get(url, timeout=15)
            root = ET.fromstring(response.content)
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
            await asyncio.sleep(300)
        except Exception as e:
            print(f"News Error: {e}")
            await asyncio.sleep(60)

async def start_fb_bot():
    application = Application.builder().token(FB_TOKEN).build()
    
    # ချန်နယ်ထဲသို့ အောင်မြင်ကြောင်း အချက်ပေးစာ ပို့ခြင်း
    try:
        await application.bot.send_message(
            chat_id=FOOTBALL_CHANNEL_ID, 
            text="✅ **Football Bot Connection Successful!**\n\nဒီချန်နယ်ထဲကို သတင်းအသစ်တွေ စတင်ပို့ပေးတော့မှာ ဖြစ်ပါတယ်ဗျာ။"
        )
    except Exception as e:
        print(f"Send to Channel Failed: {e}")

    async with application:
        await application.initialize()
        await application.start()
        asyncio.create_task(fetch_football_news(application))
        await asyncio.Event().wait()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    try:
        asyncio.run(start_fb_bot())
    except KeyboardInterrupt:
        pass 
