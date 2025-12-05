import io
import sqlite3
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.buttons import main_menu, tasks_menu, persona_menu
from bot.memory_engine import build_memory_context
from bot.utils import (
    save_user,
    log_event,
    append_conv,
    set_memory,
    get_persona,
    set_persona,
)
from services.groq_service import groq_completion
from services.image_handler import generate_image
from services.speech_to_text import transcribe_voice
from services.voice_reply import tts_audio


DB_PATH = "data/bot_data.db"


# ---------------------- START ----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user)

    await update.message.reply_text(
        "Hi — I'm **Ultimate Groq Bot** 🤖\nChoose an option:",
        reply_markup=main_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

    log_event(user.id, user.username, "start")


# ---------------------- HELP ----------------------
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (
        "**Available Commands**\n\n"
        "/ai <text> — Chat with AI\n"
        "/ai <text> --voice — Chat + voice reply\n"
        "/image <prompt> — Generate image\n"
        "/remember <fact> — Save memory\n"
        "/tasks — View tasks\n"
        "/addtask <text> — Add a task\n"
        "/cleartasks — Clear tasks\n"
    )

    await update.message.reply_text(txt, parse_mode=ParseMode.MARKDOWN)
    log_event(update.effective_user.id, update.effective_user.username, "help")


# ---------------------- AI CHAT ----------------------
async def ai_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    full_text = update.message.text

    # Extract prompt
    prompt = full_text.replace("/ai", "").replace("--voice", "").strip()

    if not prompt:
        await update.message.reply_text("Usage: /ai <your question>")
        return

    send_voice = "--voice" in full_text

    append_conv(user.id, "user", prompt)

    # Build context memory + persona + conversation summary
    memory_context = build_memory_context(user.id)

    messages = [
        {"role": "system", "content": memory_context},
        {"role": "user", "content": prompt}
    ]

    thinking_msg = await update.message.reply_text("Thinking...")

    try:
        reply_text = await groq_completion(messages)
    except Exception as e:
        await thinking_msg.delete()
        await update.message.reply_text(f"❌ Groq Error:\n{str(e)}")
        return

    await thinking_msg.delete()

    await update.message.reply_text(reply_text)
    append_conv(user.id, "assistant", reply_text)
    log_event(user.id, user.username, "ai")

    # Optional TTS
    if send_voice:
        audio = await tts_audio(reply_text)
        await update.message.reply_voice(voice=audio)


# ---------------------- IMAGE GENERATION ----------------------
async def image_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    prompt = update.message.text.replace("/image", "").strip()

    if not prompt:
        await update.message.reply_text("Usage: /image <prompt>")
        return

    await update.message.reply_text("Generating image...")

    url = await generate_image(prompt)

    if url:
        await update.message.reply_photo(photo=url, caption=f"Image for: {prompt}")
        log_event(user.id, user.username, "image")
    else:
        await update.message.reply_text("❌ Image generation failed.")


# ---------------------- VOICE → TEXT ----------------------
async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    voice_obj = update.message.voice or update.message.audio

    if not voice_obj:
        await update.message.reply_text("❌ No audio found.")
        return

    buffer = io.BytesIO()
    f = await context.bot.get_file(voice_obj.file_id)
    await f.download_to_memory(out=buffer)

    await update.message.reply_text("Transcribing...")

    text = await transcribe_voice(buffer.getvalue())

    append_conv(user.id, "user", "[voice] " + text)

    await update.message.reply_text("📝 **Transcription:**\n" + text, parse_mode="Markdown")
    log_event(user.id, user.username, "voice")


# ---------------------- TASK ADD ----------------------
async def addtask_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    task = update.message.text.replace("/addtask", "").strip()

    if not task:
        await update.message.reply_text("Usage: /addtask <task>")
        return

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("INSERT INTO tasks (user_id, task, ts) VALUES (?, ?, datetime('now'))",
                (str(user.id), task))
    con.commit()
    con.close()

    await update.message.reply_text(f"Task added: {task}", reply_markup=tasks_menu())


# ---------------------- VIEW TASKS ----------------------
async def tasks_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT id, task, ts FROM tasks WHERE user_id=? ORDER BY id DESC",
                (str(user.id),))
    rows = cur.fetchall()
    con.close()

    if not rows:
        await update.message.reply_text("No tasks yet.", reply_markup=tasks_menu())
        return

    msg = "\n".join([f"{r[0]}. {r[1]} — {r[2]}" for r in rows])
    await update.message.reply_text("**Your tasks:**\n\n" + msg, parse_mode="Markdown")


# ---------------------- CLEAR TASKS ----------------------
async def cleartasks_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("DELETE FROM tasks WHERE user_id=?", (str(user.id),))
    con.commit()
    con.close()

    await update.message.reply_text("All tasks cleared.")


# ---------------------- REMEMBER ----------------------
async def remember_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    memory_text = update.message.text.replace("/remember", "").strip()

    if not memory_text:
        await update.message.reply_text("Usage: /remember <info>")
        return

    set_memory(user.id, memory_text)
    await update.message.reply_text("Saved to permanent memory 🧠")


# ---------------------- INLINE BUTTON HANDLER ----------------------
async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    await query.answer()

    # Persona menu
    if data == "persona":
        await query.edit_message_text("Choose persona:", reply_markup=persona_menu())
        return

    # Persona change
    if data.startswith("persona_"):
        persona = data.replace("persona_", "")
        set_persona(query.from_user.id, persona)
        await query.edit_message_text(f"Persona updated to **{persona}**", parse_mode="Markdown")
        return

    # Other buttons
    if data == "ai":
        await query.edit_message_text("Send /ai <text> to chat.")
    elif data == "voice":
        await query.edit_message_text("Send a voice message to transcribe.")
    elif data == "image":
        await query.edit_message_text("Send /image <prompt> to generate image.")
    elif data == "tasks":
        await query.edit_message_text("Tasks menu:", reply_markup=tasks_menu())
    elif data == "task_add":
        await query.edit_message_text("Use /addtask <task>.")
    elif data == "task_view":
        await query.edit_message_text("Use /tasks to view tasks.")
    elif data == "task_clear":
        await query.edit_message_text("Use /cleartasks to delete tasks.")
    elif data == "back_main":
        await query.edit_message_text("Back to main menu:", reply_markup=main_menu())
    else:
        await query.edit_message_text("Unknown option.")

