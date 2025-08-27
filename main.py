from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

TOKEN = "YOUR_BOT_TOKEN"  # <-- apna token yaha daalna

# Store games {chat_id: {...}}
games = {}

# Utility: create board as inline keyboard
def make_keyboard(board):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text=("❌" if cell == "X" else "⭕" if cell == "O" else "⬜"),
                callback_data=f"{r},{c}"
            )
            for c, cell in enumerate(row)
        ]
        for r, row in enumerate(board)
    ])

# Check winner
def check_winner(board):
    for p in ["X", "O"]:
        # Rows & Cols
        for i in range(3):
            if all(board[i][j] == p for j in range(3)) or all(board[j][i] == p for j in range(3)):
                return p
        # Diagonals
        if all(board[i][i] == p for i in range(3)) or all(board[i][2 - i] == p for i in range(3)):
            return p
    return None

# -------- Commands -------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to XO Game Bot!\nPress /xo to start a new game."
    )

async def xo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    games[chat_id] = {
        "board": [[None]*3 for _ in range(3)],
        "turn": "X"
    }
    await update.message.reply_text(
        "🎮 XO Game started!\n❌ goes first.",
        reply_markup=make_keyboard(games[chat_id]["board"])
    )

# -------- Handle Button Clicks -------- #
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id

    if chat_id not in games:
        await query.edit_message_text("⚠️ Game not found. Start with /xo")
        return

    game = games[chat_id]
    board, turn = game["board"], game["turn"]

    r, c = map(int, query.data.split(","))
    if board[r][c] is not None:
        return  # already filled

    # Place move
    board[r][c] = turn
    winner = check_winner(board)

    if winner:
        await query.edit_message_text(
            f"🏆 {winner} wins!",
            reply_markup=make_keyboard(board)
        )
        del games[chat_id]
    elif all(cell is not None for row in board for cell in row):
        await query.edit_message_text(
            "🤝 It's a draw!",
            reply_markup=make_keyboard(board)
        )
        del games[chat_id]
    else:
        game["turn"] = "O" if turn == "X" else "X"
        await query.edit_message_text(
            f"{turn} played! Now {game['turn']}'s turn.",
            reply_markup=make_keyboard(board)
        )

# -------- Main -------- #
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("xo", xo))
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()

if __name__ == "__main__":
    main()
