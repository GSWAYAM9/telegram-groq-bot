
PERSONAS = {
    "professional": "You speak concisely, formally and clearly.",
    "friendly": "You speak warmly, casually and happily.",
    "romantic": "You speak softly, emotionally and affectionately.",
    "sarcastic": "You use witty sarcasm in your replies.",
    "coder": "You speak like a senior software engineer and use code examples.",
    "funny": "You respond with humor and jokes.",
}


def get_persona_instruction(persona: str) -> str:
    return PERSONAS.get(persona, PERSONAS["professional"])
