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

# --- ဒီနေရာမှာ လူကြီးမင်း စိတ်ကြိုက် စာသားတွေ ပြောင်းနိုင်ပါတယ် ---
MATCH_ANALYSIS = """
📊 **ဒီနေ့ပွဲစဉ် သုံးသပ်ချက် (၂၇ ဧပြီ)**

⚽ **Arsenal vs Chelsea**
အာဆင်နယ်က အိမ်ကွင်းမှာ ခြေစွမ်းပြနေပြီး ချဲလ်ဆီးကတော့ ရုန်းကန်နေရပါတယ်။
- ခန့်မှန်းချက်- အာဆင်နယ် အနိုင် (သို့မဟုတ်) ၂ ဂိုးပြတ်။
- အမှတ်ပေးဇယား- အာဆင်နယ်အတွက် အမှတ်က အရမ်းအရေးကြီးပါတယ်။

(မှတ်ချက်- ဒါဟာ နမူနာ သုံးသပ်ချက်သာ ဖြစ်ပါတယ်။)
"""

MATCH_LINEUP = """
📋 **ပွဲထွက်လူစာရင်း (Line-up Update)**

⚽ **Arsenal XI:** Raya; White, Saliba, Gabriel, Tomiyasu; Rice, Partey, Odegaard; Saka, Havertz, Trossard.

⚽ **Chelsea XI:** Petrovic; Gilchrist, Disasi, Badiashile, Cucurella; Caicedo, Enzo; Madueke, Gallagher, Mudryk; Jackson.
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
        "⚽ **Football Agent Expert** မှ ကြိုဆိုပါတယ်။\nသင့်အတွက် အကောင်းဆုံး သုံးသပ်ချက်နဲ့ လင့်ခ်များ အသင့်ရှိနေပါပြီ။",
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
        link_keyboard = [
            [InlineKeyboardButton("📱 ဖုန်းဖြင့်ကြည့်ရန် (Link 1)", url="https://koora4live.to/")],
            [InlineKeyboardButton("💻 PC ဖြင့်ကြည့်ရန် (Link 2)", url="https://yalla-shoot.io/")],
            [InlineKeyboardButton("📺 Backup Link (Link 3)", url="https://www.totalsportek.to/")]
        ]
        reply_markup = InlineKeyboardMarkup(link_keyboard)
        await query.edit_message_text(text="🔗 **ကြည့်ရှုရန် လင့်ခ်များ**\nပွဲချိန်တွင် အောက်ပါလင့်ခ်များကို နှိပ်၍ ကြည့်ရှုနိုင်ပါသည်-", reply_markup=reply_markup, parse_mode='Markdown')

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling(drop_pending_updates=True) 
