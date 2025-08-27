import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Get environment variables
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://xo-telegram-bot.onrender.com

# ---- Commands ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Hello {update.effective_user.first_name}! 👋\n"
        f"XO Bot is live on Render ✅"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /start to begin.\nMore features coming soon!")

# ---- Main ----
def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN not set in environment variables")

    app = Application.builder().token(TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Webhook mode for Render
    if WEBHOOK_URL:
        app.run_webhook(
            listen="0.0.0.0",
            port=int(os.getenv("PORT", 8000)),
            url_path=TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{TOKEN}",
        )
    else:
        # Local testing
        app.run_polling()

if __name__ == "__main__":
    main()
    
