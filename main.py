import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# --- CONFIGURATION ---
TOKEN = os.environ.get("BOT_TOKEN")
# လူကြီးမင်း၏ Channel ID အစစ်အမှန်
CHANNEL_ID = -1003706871581 

app = Flask(__name__)

@app.route("/")
def home():
    return "Football Agent is Active!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Channel ထဲသို့ ပို့မည့် သတင်းစာသား ---
POST_MESSAGE = """
⚽ **MATCH DAY PREVIEW**
━━━━━━━━━━━━━━━
🏆 **Serie A & La Liga (ဧပြီ ၂၇)**

📊 **Lazio vs Verona** (၁:၁၅ AM)
လာဇီယို အိမ်ကွင်းမှာ အမှတ်အပြည့်ယူဖို့ များပါတယ်။
- ခန့်မှန်းချက်- လာဇီယို နိုင်။

📊 **Atletico Madrid vs Bilbao** (၁:၃၀ AM)
နှစ်သင်းလုံး အကြိတ်အနယ်ဖြစ်မယ့်ပွဲပါ။
- ခန့်မှန်းချက်- ဂိုးနည်း သရေ (သို့) အက်သလက်တီကို နိုင်။

🔗 **Live Links (ကြည့်ရန်):**
1. [Server 1 - Yalla Shoot](https://yallashoot.video/)
2. [Server 2 - Live Soccer](https://www.livesoccertv.com/)
3. [Server 3 - Yalla Live](https://yalla-live.tv/)
━━━━━━━━━━━━━━━
"""

# --- BOT FUNCTIONS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽ Football Agent Bot မှ ကြိုဆိုပါတယ်။\n\n"
        "Channel ထဲကို ဒီနေ့ပွဲစဉ်သတင်းများ ပို့ချင်ရင် `/post` လို့ ရိုက်ပေးပါဗျ။"
    )

async def post_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Channel ထဲသို့ တိုက်ရိုက်စာပို့ခြင်း
        await context.bot.send_message(
            chat_id=CHANNEL_ID, 
            text=POST_MESSAGE, 
            parse_mode='Markdown', 
            disable_web_page_preview=True
        )
        await update.message.reply_text("✅ Channel ထဲကို သတင်းပို့ပြီးပါပြီဗျာ!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}\nBot ကို Channel Admin ခန့်ထားတာ သေချာရဲ့လား ပြန်စစ်ပေးပါဦးဗျ။")

if __name__ == "__main__":
    # Web server start
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Bot polling start
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("post", post_to_channel))
    
    print("Football Agent is starting...")
    application.run_polling(drop_pending_updates=True) 
