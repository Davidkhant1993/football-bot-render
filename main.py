import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- CONFIGURATION ---
# လူကြီးမင်းရဲ့ Football Bot Token ကို ဒီမှာ အစားထိုးပါ
TOKEN = "FOOTBALL_BOT_TOKEN_ဒီမှာထည့်ပါ"

# --- WEB SERVER FOR RENDER ---
app = Flask(__name__)

@app.route("/")
def home():
    return "Football Bot is Alive!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- BOT COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚽ Football Bot မှ ကြိုဆိုပါတယ်။ Render ပေါ်မှာ ၂၄ နာရီ အလုပ်လုပ်နေပါပြီ!")

async def test_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot အလုပ်လုပ်နေပါတယ်။ Test အောင်မြင်ပါတယ်!")

# --- MAIN RUN ---
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("Football Bot is starting...")
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("test", test_post))
    application.run_polling(drop_pending_updates=True)
