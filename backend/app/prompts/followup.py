LANG_INSTRUCTIONS = {
    "ru": "Отвечай на русском языке.",
    "ua": "Відповідай українською мовою.",
    "en": "Reply in English.",
    "bg": "Отговаряй на български език.",
}

RESULT_MAP = {
    "liked": "объект понравился клиенту",
    "disliked": "объект не понравился клиенту",
    "thinking": "клиент думает, не принял решение",
}


def build_prompt(params: dict, language: str) -> str:
    lang = LANG_INSTRUCTIONS.get(language, LANG_INSTRUCTIONS["ru"])
    result = RESULT_MAP.get(params.get("viewing_result", "thinking"), params.get("viewing_result", ""))
    client_feedback = params.get("client_feedback", "")

    return f"""{lang}
Ты профессиональный риелтор. Напиши персонализированное follow-up сообщение клиенту в мессенджер после просмотра.

Результат просмотра: {result}
Что сказал клиент: {client_feedback}

Требования:
- Короткое (5-8 предложений)
- Тёплый, человечный тон
- Упомяни конкретику из просмотра если есть
- Если понравилось — мягко подтолкни к следующему шагу
- Если не понравилось — предложи альтернативу
- Если думает — дай пространство и предложи помощь
- Без давления, без шаблонных фраз"""
