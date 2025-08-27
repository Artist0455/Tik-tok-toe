from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import random

TOKEN = "8329813270:AAGuT6N_K3I1NkxiClAO8qcD4XeWIi0D4es"   # <-- apna token yaha daalna

# XO game board storage
games = {}

# Utility: display board
def render_board(board):
    symbols = {None: "⬜", "X": "❌", "O": "⭕"}
    return "\n".join("".join(symbols[cell] for cell in row) for row in board)

# Check winner
def check_winner(board):
    for p in ["X", "O"]:
        # Rows & Cols
        for i in range(3):
            if all(board[i][j] == p for j in range(3)) or all(board[j][i] == p for j in range(3)):
                return p
        # Diagonals
        if all(board[i][i] == p for i in range(3)) or all(board[i][2-i] == p for i in range(3)):
            return p
    return None

# -------- Commands -------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"👋 Hello {user.mention_html()}! Welcome to XO Bot.\n\nUse /help to see all commands."
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📜 Commands:\n"
        "/start - Welcome message\n"
        "/help - Show commands\n"
        "/echo <text> - Repeat text\n"
        "/dice - Roll a dice 🎲\n"
        "/rps - Rock Paper Scissors ✊🖐✌️\n"
        "/xo - Start a new XO (tic-tac-toe) game\n"
        "/move <row> <col> - Play your move (1-3 each)\n"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        await update.message.reply_text(" ".join(context.args))
    else:
        await update.message.reply_text("⚠️ Please provide some text.")

async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    num = random.randint(1, 6)
    await update.message.reply_text(f"🎲 You rolled: {num}")

async def rps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = random.choice(["✊ Rock", "🖐 Paper", "✌ Scissors"])
    await update.message.reply_text(f"🤖 Bot chose: {choice}")

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"🎉 Welcome {member.full_name}! Enjoy your stay.")

# -------- XO Game -------- #

async def xo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    # New game board
    games[chat_id] = {
        "board": [[None]*3 for _ in range(3)],
        "turn": "X"
    }
    await update.message.reply_text(
        "🎮 XO Game started!\n❌ goes first.\n\n" + render_board(games[chat_id]["board"]) +
        "\n\nPlay with: /move row col (example: /move 1 2)"
    )

async def move(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in games:
        await update.message.reply_text("⚠️ No game running. Start with /xo")
        return

    game = games[chat_id]
    board, turn = game["board"], game["turn"]

    try:
        r, c = int(context.args[0])-1, int(context.args[1])-1
    except:
        await update.message.reply_text("⚠️ Usage: /move row col (1-3 each)")
        return

    if not (0 <= r < 3 and 0 <= c < 3):
        await update.message.reply_text("⚠️ Invalid position (use 1-3).")
        return
    if board[r][c] is not None:
        await update.message.reply_text("⚠️ Cell already taken.")
        return

    # Place move
    board[r][c] = turn
    winner = check_winner(board)

    if winner:
        await update.message.reply_text(
            f"🏆 {winner} wins!\n\n{render_board(board)}"
        )
        del games[chat_id]
    elif all(cell is not None for row in board for cell in row):
        await update.message.reply_text(
            f"🤝 Draw!\n\n{render_board(board)}"
        )
        del games[chat_id]
    else:
        # Next turn
        game["turn"] = "O" if turn == "X" else "X"
        await update.message.reply_text(
            f"{turn} played!\nNow {game['turn']}'s turn.\n\n{render_board(board)}"
        )

# -------- Main -------- #

def main():
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("echo", echo))
    app.add_handler(CommandHandler("dice", dice))
    app.add_handler(CommandHandler("rps", rps))
    app.add_handler(CommandHandler("xo", xo))
    app.add_handler(CommandHandler("move", move))

    # Welcome new members
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    app.run_polling()

if __name__ == "__main__":
    main()
    
