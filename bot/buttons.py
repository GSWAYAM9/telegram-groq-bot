from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 AI Chat", callback_data="ai")],
        [InlineKeyboardButton("🎙 Voice Input", callback_data="voice")],
        [InlineKeyboardButton("🖼 Image Gen", callback_data="image")],
        [InlineKeyboardButton("📝 Tasks", callback_data="tasks")],
        [InlineKeyboardButton("🎭 Persona", callback_data="persona")],
        [InlineKeyboardButton("ℹ Help", callback_data="help")]
    ])


def tasks_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Task", callback_data="task_add")],
        [InlineKeyboardButton("📋 View Tasks", callback_data="task_view")],
        [InlineKeyboardButton("❌ Clear Tasks", callback_data="task_clear")],
        [InlineKeyboardButton("⬅ Back", callback_data="back_main")]
    ])


def persona_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👔 Professional", callback_data="persona_professional")],
        [InlineKeyboardButton("😊 Friendly", callback_data="persona_friendly")],
        [InlineKeyboardButton("❤️ Romantic", callback_data="persona_romantic")],
        [InlineKeyboardButton("😎 Sarcastic", callback_data="persona_sarcastic")],
        [InlineKeyboardButton("👨‍💻 Coder", callback_data="persona_coder")],
        [InlineKeyboardButton("😂 Funny", callback_data="persona_funny")],
        [InlineKeyboardButton("⬅ Back", callback_data="back_main")]
    ])
