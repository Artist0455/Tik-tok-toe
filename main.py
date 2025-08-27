import os
import logging
from typing import Dict, Optional, List

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ============ Logging ============
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ============ Game State ============
class GameState:
    def __init__(self):
        self.board: List[str] = [' '] * 9
        self.players: Dict[int, str] = {}
        self.turn: str = 'X'
        self.winner: Optional[str] = None
        self.finished: bool = False

    def reset(self):
        self.board = [' '] * 9
        self.players = {}
        self.turn = 'X'
        self.winner = None
        self.finished = False

    @staticmethod
    def win_lines():
        return [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]

    def check_winner(self):
        for a, b, c in self.win_lines():
            if self.board[a] != ' ' and self.board[a] == self.board[b] == self.board[c]:
                self.winner = self.board[a]
                self.finished = True
                return
        if ' ' not in self.board:
            self.winner = None
            self.finished = True

    def assign_player(self, user_id: int) -> str:
        if user_id in self.players:
            return self.players[user_id]
        if 'X' not in self.players.values():
            self.players[user_id] = 'X'
        elif 'O' not in self.players.values():
            self.players[user_id] = 'O'
        else:
            self.players.setdefault(user_id, '-')
        return self.players[user_id]

    def can_play(self, user_id: int) -> bool:
        sym = self.players.get(user_id)
        return sym in ('X', 'O') and sym == self.turn and not self.finished

    def make_move(self, idx: int, symbol: str) -> bool:
        if 0 <= idx < 9 and self.board[idx] == ' ' and not self.finished and symbol == self.turn:
            self.board[idx] = symbol
            self.check_winner()
            if not self.finished:
                self.turn = 'O' if self.turn == 'X' else 'X'
            return True
        return False

# In-memory games per chat_id
GAMES: Dict[int, GameState] = {}
XO = { 'X': '❌', 'O': '⭕', ' ': '▫️' }

# ============ UI helpers ============
def board_markup(gs: GameState, chat_id: int) -> InlineKeyboardMarkup:
    buttons = []
    for r in range(3):
        row = []
        for c in range(3):
            i = r * 3 + c
            cell = gs.board[i]
            text = XO[cell]
            cb = f"mv:{chat_id}:{i}"
            row.append(InlineKeyboardButton(text=text, callback_data=cb))
        buttons.append(row)
    controls = [[InlineKeyboardButton("🔄 New Game", callback_data=f"reset:{chat_id}")]]
    return InlineKeyboardMarkup(buttons + controls)

def status_text(gs: GameState) -> str:
    if gs.finished:
        if gs.winner is None:
            return "Game over! It’s a draw."
        return f"Game over! Winner: {XO[gs.winner]}"
    else:
        return f"Turn: {XO[gs.turn]}"

# ============ Command Handlers ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    gs = GAMES.setdefault(chat_id, GameState())
    text = (
        "Welcome to XO (Tic-Tac-Toe)!\n\n"
        "How to play:\n"
        "• First tapper becomes ❌, second becomes ⭕.\n"
        "• Players take turns. Whoever makes a line wins.\n"
        "• Use /newgame to start fresh.\n\n"
        "This bot runs on Render Web Service."
    )
    await update.message.reply_text(text, reply_markup=board_markup(gs, chat_id))

async def newgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    gs = GAMES.setdefault(chat_id, GameState())
    gs.reset()
    await update.message.reply_text("New game! ❌ starts.", reply_markup=board_markup(gs, chat_id))

# ============ Callback Handlers ============
async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.callback_query:
        return
    q = update.callback_query
    data = q.data or ""

    try:
        action, chat_id_str, *rest = data.split(":")
        chat_id = int(chat_id_str)
    except Exception:
        await q.answer()
        return

    gs = GAMES.setdefault(chat_id, GameState())
    user_id = q.from_user.id

    if action == "reset":
        gs.reset()
        await q.answer("New board ready!")
        await q.edit_message_reply_markup(reply_markup=board_markup(gs, chat_id))
        return

    if action == "mv":
        sym = gs.assign_player(user_id)
        if sym not in ("X", "O"):
            await q.answer("Two players already in!", show_alert=True)
            return
        if not gs.can_play(user_id):
            await q.answer("Not your turn!", show_alert=False)
            return

        try:
            idx = int(rest[0])
        except Exception:
            await q.answer()
            return

        if gs.make_move(idx, sym):
            await q.answer()
            caption = status_text(gs)
            try:
                await q.edit_message_caption(caption)
            except Exception:
                pass
            await q.edit_message_reply_markup(reply_markup=board_markup(gs, chat_id))
        else:
            await q.answer("Invalid move!", show_alert=False)

# ============ Webhook bootstrap ============
async def post_init(app: Application):
    await app.bot.set_my_commands([
        ("start", "Show help & current board"),
        ("newgame", "Start a new game"),
    ])

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN env var is required")

    base_url = os.environ.get("WEBHOOK_URL")
    if not base_url:
        raise RuntimeError("WEBHOOK_URL env var is required")

    port = int(os.environ.get("PORT", "10000"))
    application = Application.builder().token(token).post_init(post_init).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("newgame", newgame))
    application.add_handler(CallbackQueryHandler(on_button))

    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=token,
        webhook_url=f"{base_url}/{token}",
        drop_pending_updates=True,
    )

if __name__ == "__main__":
    main()
