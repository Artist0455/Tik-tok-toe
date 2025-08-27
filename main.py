from telegram import Update, ChatMember
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    ContextTypes,
    filters
)
import random

TOKEN = "YOUR_BOT_TOKEN"  # <-- yaha apna bot token daalna

# ---------------- COMMANDS ---------------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"👋 Hello {user.mention_html()}! Welcome to XO Bot.\n\n"
        "Use /help to see all commands."
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📜 Available Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/echo <text> - Repeat your text\n"
        "/dice - Roll a dice 🎲\n"
        "/rps - Play Rock-Paper-Scissors ✊🖐✌️"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        text = " ".join(context.args)
        await update.message.reply_text(text)
    else:
        await update.message.reply_text("⚠️ Please provide some text.")

async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    num = random.randint(1, 6)
    await update.message.reply_text(f"🎲 You rolled: {num}")

async def rps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = random.choice(["✊ Rock", "🖐 Paper", "✌ Scissors"])
    await update.message.reply_text(f"🤖 Bot chose: {choice}")

# ---------------- WELCOME NEW MEMBERS ---------------- #
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"🎉 Welcome {member.full_name}! Enjoy your stay."
        )

# ---------------- MAIN ---------------- #
def main():
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("echo", echo))
    app.add_handler(CommandHandler("dice", dice))
    app.add_handler(CommandHandler("rps", rps))

    # Welcome message when new user joins
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    # Run the bot
    app.run_polling()

if __name__ == "__main__":
    main()
    
