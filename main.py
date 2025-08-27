from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import random

TOKEN = "YOUR_BOT_TOKEN"  # <-- apna token yaha daalo

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"👋 Hello {user.mention_html()}! Welcome to XO Bot.\n\nUse /help to see all commands."
    )

# Help command
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📜 Commands:\n"
        "/start - Welcome message\n"
        "/help - Show commands\n"
        "/echo <text> - Repeat text\n"
        "/dice - Roll a dice 🎲\n"
        "/rps - Rock Paper Scissors ✊🖐✌️"
    )

# Echo command
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        await update.message.reply_text(" ".join(context.args))
    else:
        await update.message.reply_text("⚠️ Please provide some text.")

# Dice game
async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    num = random.randint(1, 6)
    await update.message.reply_text(f"🎲 You rolled: {num}")

# Rock Paper Scissors
async def rps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = random.choice(["✊ Rock", "🖐 Paper", "✌ Scissors"])
    await update.message.reply_text(f"🤖 Bot chose: {choice}")

# Welcome new users
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"🎉 Welcome {member.full_name}! Enjoy your stay.")

def main():
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("echo", echo))
    app.add_handler(CommandHandler("dice", dice))
    app.add_handler(CommandHandler("rps", rps))

    # Welcome new members
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    app.run_polling()

if __name__ == "__main__":
    main()
    
