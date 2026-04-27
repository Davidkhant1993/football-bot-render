import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# --- CONFIGURATION ---
TOKEN = os.environ.get("BOT_TOKEN")

app = Flask(__name__)

@app.route("/")
def home():
    return "Football Expert Bot is Running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- BOT FUNCTIONS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 ပွဲကြိုသုံးသပ်ချက်", callback_data='analysis')],
        [InlineKeyboardButton("📋 လူစာရင်း (Line-up)", callback_data='lineup')],
        [InlineKeyboardButton("🔗 တိုက်ရိုက်ကြည့်ရန်လင့်ခ်များ", callback_data='links')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "⚽ Football Agent မှ ကြိုဆိုပါတယ်။\nဘာများ အကူအညီပေးရမလဲခင်ဗျာ?",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'analysis':
        await query.edit_message_text(text="📊 **ပွဲကြိုသုံးသပ်ချက်**\n\n(ဒီနေရာမှာ အနိုင်/အရှုံး/သရေ ခန့်မှန်းချက်တွေကို ထည့်သွင်းပေးပါမည်။)")
    
    elif query.data == 'lineup':
        await query.edit_message_text(text="📋 **လူစာရင်း (Line-up)**\n\n(ပွဲမစခင် ထွက်ပေါ်လာမည့် လူစာရင်းများကို ဤနေရာတွင် ကြည့်ရှုနိုင်ပါသည်။)")

    elif query.data == 'links':
        link_keyboard = [
            [InlineKeyboardButton("📱 ဖုန်းဖြင့်ကြည့်ရန်", url="https://yourlink1.com")],
            [InlineKeyboardButton("💻 PC ဖြင့်ကြည့်ရန်", url="https://yourlink2.com")],
            [InlineKeyboardButton("📺 Backup Link", url="https://yourlink3.com")]
        ]
        reply_markup = InlineKeyboardMarkup(link_keyboard)
        await query.edit_message_text(text="🔗 **ကြည့်ရှုရန် လင့်ခ်များ**\nသင့်စက်ပစ္စည်းအလိုက် ရွေးချယ်ကြည့်ရှုနိုင်ပါသည်-", reply_markup=reply_markup)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    
    print("Football Expert Bot is starting...")
    application.run_polling(drop_pending_updates=True) 
