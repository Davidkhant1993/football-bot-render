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

# --- ပွဲစဉ်အလိုက် လင့်ခ်များ ရှာပေးမည့်စနစ် ---
def get_live_links(match_name):
    # လူကြီးမင်းအတွက် အမြဲတမ်း အလုပ်လုပ်မယ့် Global Streaming Links တွေကို ရှာဖွေပေးထားပါတယ်
    search_query = match_name.replace(" ", "+")
    links = [
        f"🔗 [Server 1 - Yalla Shoot](https://yalla-shoot.com/search?q={search_query})",
        f"🔗 [Server 2 - Live Soccer](https://www.livesoccertv.com/search/?q={search_query})",
        f"🔗 [Server 3 - Yalla Live](https://yallalive.org/)"
    ]
    return "\n".join(links)

async def auto_post_preview(application):
    # ဒါက Bot ကနေ အလိုအလျောက် ပို့ပေးမယ့် ပုံစံပါ
    # တကယ့် API နဲ့ ချိတ်တဲ့အခါ ပွဲနာမည်တွေ အလိုအလျောက် ပြောင်းသွားပါမယ်
    match_name = "Real Madrid vs Barcelona"
    links = get_live_links(match_name)
    
    msg = (
        f"⚽ **MATCH DAY PREVIEW**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🏟 **{match_name}**\n\n"
        f"📋 **Line-up ကြိုတင်ခန့်မှန်းချက်**\n"
        f"• Bot က သတင်းဌာနများမှ နောက်ဆုံးရ လူစာရင်းကို အလိုအလျောက် စုစည်းဖော်ပြပေးပါမည်။\n\n"
        f"🎯 **အနိုင်/အရှုံး ခန့်မှန်းချက်**\n"
        f"• အချက်အလက်များအရ အိမ်ကွင်းအသင်းက ၆၀% အနိုင်ရရှိရန် အခွင့်အလမ်းရှိပါသည်။\n\n"
        f"📺 **တိုက်ရိုက်ကြည့်ရှုရန် လင့်ခ်များ**\n"
        f"{links}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"_(မှတ်ချက်- ဒါဟာ နမူနာ သုံးသပ်ချက်သာ ဖြစ်ပါတယ်။)_"
    )
    
    await asyncio.sleep(10) # Deploy ပြီး ၁၀ စက္ကန့်နေရင် ပို့မည်
    await application.bot.send_message(chat_id=FOOTBALL_CHANNEL_ID, text=msg, parse_mode='Markdown')

async def start_fb_bot():
    application = Application.builder().token(FB_TOKEN).build()
    async with application:
        await application.initialize()
        await application.start()
        
        # နမူနာကို အရင်ပို့ခိုင်းခြင်း
        asyncio.create_task(auto_post_preview(application))
        
        await asyncio.Event().wait()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    try:
        asyncio.run(start_fb_bot())
    except KeyboardInterrupt:
        pass 
