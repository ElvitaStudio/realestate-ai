LANG_INSTRUCTIONS = {
    "ru": "Отвечай на русском языке.",
    "ua": "Відповідай українською мовою.",
    "en": "Reply in English.",
    "bg": "Отговаряй на български език.",
}

TONE_MAP = {
    "emotional": "эмоциональный и вдохновляющий",
    "business": "деловой и профессиональный",
    "premium": "премиальный и статусный",
}


def build_prompt(params: dict, language: str) -> str:
    lang = LANG_INSTRUCTIONS.get(language, LANG_INSTRUCTIONS["ru"])
    tone = TONE_MAP.get(params.get("tone", "emotional"), "эмоциональный")
    emoji = "Добавь уместные эмодзи." if params.get("use_emoji") else "Не используй эмодзи."

    return f"""{lang}
Ты профессиональный SMM-специалист для риелторов. Напиши пост для Instagram.

Объект: {params.get("property_description", "")}
Тон: {tone}
{emoji}

Требования:
- Длина до 2200 символов
- В конце добавь 15–20 релевантных хэштегов на языке поста
- Первые 2 строки должны цеплять — они видны без раскрытия
- Включи призыв к действию (написать в директ, позвонить)"""
