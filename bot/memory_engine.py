
import sqlite3
from config import DB_PATH
from bot.utils import get_conv_history, get_memory, get_persona
from bot.persona import get_persona_instruction

MAX_CTX = 4000  # safe limit


def build_memory_context(user_id: str) -> str:
    """Build persona + permanent memory + recent conversation history."""

    persona = get_persona(user_id)
    persona_block = f"Persona:\n{get_persona_instruction(persona)}\n\n"

    perm = get_memory(user_id)
    mem_block = f"Permanent Memory:\n{perm}\n\n" if perm else ""

    history = get_conv_history(user_id, limit=30)

    convo = ""
    for h in history:
        convo += f"{h['role']}: {h['content']}\n"

    convo_block = f"Conversation:\n{convo}\n"

    final = persona_block + mem_block + convo_block

    if len(final) > MAX_CTX:
        return final[-MAX_CTX:]

    return final
