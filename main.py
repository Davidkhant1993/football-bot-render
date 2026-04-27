import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is Running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚽ Football Bot အလုပ်လုပ်နေပါပြီဗျာ!")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling(drop_pending_updates=True) 
