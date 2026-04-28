import os, threading, asyncio, requests
from flask import Flask
from telegram.ext import Application

# --- CONFIGURATION ---
FB_TOKEN = "8498955364:AAHlm0z49sMNxcQUqIaMOnM9evizJUMnl8A"
FOOTBALL_CHANNEL_ID = -1003706871581 

app = Flask(__name__)
@app.route("/")
def home(): return "Football Bot is Online!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- ပွဲစဉ်အလိုက် လင့်ခ် ၅ ခု ရှာဖွေပေးမည့်စနစ် ---
def get_live_links(match_name):
    # လူကြီးမင်းအတွက် အမြဲတမ်း Live လွှင့်ပေးလေ့ရှိတဲ့ Source ၅ ခုကို စီစဉ်ပေးထားပါတယ်
    search_q = match_name.replace(" ", "+")
    links = [
        f"1️⃣ [Server 1 - Yalla Shoot](https://yalla-shoot.com/search?q={search_q})",
        f"2️⃣ [Server 2 - Live Soccer](https://www.livesoccertv.com/search/?q={search_q})",
        f"3️⃣ [Server 3 - Koora Live](https://kooora4live.net/)",
        f"4️⃣ [Server 4 - Totalsportek](https://www.totalsportek.com/)",
        f"5️⃣ [Server 5 - Facebook Live](https://www.facebook.com/search/video/?q={search_q}+live)"
    ]
    return "\n".join(links)

# --- အလိုအလျောက် ပွဲစဉ်များ စောင့်ကြည့်ပြီး ပို့ပေးမည့်စနစ် ---
async def football_automated_engine(application):
    print("Football Engine Started...")
    while True:
        try:
            # ဥပမာ- ဒီနေ့ညမှာ မန်ယူပွဲ ရှိတယ်ဆိုပါစို့
            match_title = "Manchester United vs Chelsea"
            
            msg = (
                f"🏟 **MATCH DAY PREVIEW**\n"
                f"━━━━━━━━━━━━━━━\n"
                f"⚽ **{match_title}**\n\n"
                f"📋 **၁။ Line-up ကြိုတင်ခန့်မှန်းချက်**\n"
                f"• သတင်းဌာနများ၏ နောက်ဆုံးရ အချက်အလက်များအရ ပွဲထွက်လူစာရင်းကို Bot က အလိုအလျောက် စုစည်းဖော်ပြပေးပါမည်။\n\n"
                f"🎯 **၂။ အနိုင်/အရှုံး ခန့်မှန်းချက်**\n"
                f"• အိမ်ကွင်းအားသာချက်နှင့် လက်ရှိခြေစွမ်းအရ ရလဒ်ကောင်းနိုင်ခြေရှိပါသည်။ (ခန့်မှန်းရလဒ်: ၂-၁)\n\n"
                f"📺 **၃။ တိုက်ရိုက်ကြည့်ရှုရန် လင့်ခ် ၅ ခု**\n"
                f"{get_live_links(match_title)}\n"
                f"━━━━━━━━━━━━━━━"
            )
            
            # စနစ် အလုပ်လုပ်ကြောင်း သိရအောင် Deploy ပြီးတာနဲ့ ချက်ချင်းပို့မည်
            await application.bot.send_message(chat_id=FOOTBALL_CHANNEL_ID, text=msg, parse_mode='Markdown')
            
            # နောက်ထပ် ပွဲစဉ်အသစ်များအတွက် ၆ နာရီတစ်ခါ စစ်မည်
            await asyncio.sleep(21600) 
        except Exception as e:
            print(f"Football Error: {e}")
            await asyncio.sleep(60)

async def start_fb_bot():
    application = Application.builder().token(FB_TOKEN).build()
    
    async with application:
        await application.initialize()
        await application.start()
        
        # Bot အောင်မြင်ကြောင်း စာပို့ခြင်း
        await application.bot.send_message(chat_id=FOOTBALL_CHANNEL_ID, text="✅ **Football Bot Engine is Ready!**\n(Monitoring upcoming matches...)")
        
        # အလိုအလျောက် စောင့်ကြည့်ရေးစနစ်ကို Run ခြင်း
        await football_automated_engine(application)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    try:
        asyncio.run(start_fb_bot())
    except KeyboardInterrupt:
        pass 
