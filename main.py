import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = os.environ.get("BOT_TOKEN")

app = Flask(__name__)

@app.route("/")
def home():
    return "Football Agent Expert is Online!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- ဒီနေ့ပွဲစဉ်အတွက် အချက်အလက်များ (ဧပြီ ၂၇) ---
# ဒီစာသားတွေကို GitHub မှာ အချိန်မရွေး ပြောင်းလို့ရပါတယ်
MATCH_ANALYSIS = """
📊 **ဒီနေ့ပွဲစဉ် သုံးသပ်ချက် (ဧပြီ ၂၇)**

🇮🇹 **Lazio vs Verona** (၁:၁၅ AM)
လာဇီယိုက အိမ်ကွင်းမှာ အမှတ်လိုအပ်နေသလို ခြေစွမ်းလည်း ပိုသာပါတယ်။
- ခန့်မှန်းချက်- လာဇီယို အနိုင်။

🇪🇸 **Atletico Madrid vs Bilbao** (၁:၃၀ AM)
ချန်ပီယံလိဂ်ဝင်ခွင့်အတွက် နှစ်သင်းလုံး အသေအလဲ ကစားမယ့်ပွဲပါ။
- ခန့်မှန်းချက်- ဂိုးနည်း သရေ (သို့မဟုတ်) အက်သလက်တီကို ကပ်နိုင်။
"""

MATCH_LINEUP = """
📋 **ပွဲထွက်လူစာရင်း Update**

Lazio နှင့် Atletico Madrid တို့၏ လူစာရင်းများသည် ပွဲမစမီ နာရီဝက်အလိုတွင် တရားဝင်ထွက်ပေါ်လာပါမည်။
(Update ဖြစ်သည်နှင့် ဤနေရာတွင် တင်ပေးပါမည်။)
"""

# --- BOT FUNCTIONS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 ပွဲကြိုသုံးသပ်ချက်", callback_data='analysis')],
        [InlineKeyboardButton("📋 လူစာရင်း (Line-up)", callback_data='lineup')],
        [InlineKeyboardButton("🔗 တိုက်ရိုက်ကြည့်ရန်လင့်ခ်များ", callback_data='links')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "⚽ **Football Agent Expert** မှ ကြိုဆိုပါတယ်။\nဒီနေ့ရဲ့ အကောင်းဆုံး သုံးသပ်ချက်နဲ့ လင့်ခ်များ အသင့်ရှိနေပါပြီ။",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'analysis':
        await query.edit_message_text(text=MATCH_ANALYSIS, parse_mode='Markdown')
    
    elif query.data == 'lineup':
        await query.edit_message_text(text=MATCH_LINEUP, parse_mode='Markdown')

    elif query.data == 'links':
        # ကြည့်လို့ရနိုင်ခြေအရှိဆုံး လင့်ခ်အသစ်များ
        link_keyboard = [
            [InlineKeyboardButton("📺 Link 1 (Yalla-Shoot)", url="https://yallashoot.video/")],
            [InlineKeyboardButton("📺 Link 2 (Live Soccer)", url="https://www.livesoccertv.com/")],
            [InlineKeyboardButton("📺 Link 3 (Yalla-Live)", url="https://yalla-live.tv/")]
        ]
        reply_markup = InlineKeyboardMarkup(link_keyboard)
        await query.edit_message_text(text="🔗 **ကြည့်ရှုရန် လင့်ခ်များ**\nLink တစ်ခု မရပါက နောက်တစ်ခု ပြောင်းကြည့်ပါ-", reply_markup=reply_markup, parse_mode='Markdown')

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling(drop_pending_updates=True) 
