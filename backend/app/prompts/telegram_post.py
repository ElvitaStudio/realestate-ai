LANG_INSTRUCTIONS = {
    "ru": "Отвечай на русском языке.",
    "ua": "Відповідай українською мовою.",
    "en": "Reply in English.",
    "bg": "Отговаряй на български език.",
}

TONE_MAP = {
    "informative": "информативный и чёткий",
    "selling": "продающий с акцентом на выгоды",
}


def build_prompt(params: dict, language: str) -> str:
    lang = LANG_INSTRUCTIONS.get(language, LANG_INSTRUCTIONS["ru"])
    tone = TONE_MAP.get(params.get("tone", "selling"), "продающий")

    return f"""{lang}
Ты профессиональный копирайтер для Telegram-каналов риелторов. Напиши пост для Telegram.

Объект: {params.get("property_description", "")}
Тон: {tone}

Требования:
- Используй форматирование Telegram: **жирный** для ключевых характеристик, __курсив__ для акцентов
- Без лишних хэштегов (максимум 3)
- Чёткая структура: заголовок → параметры → преимущества → цена → призыв к действию
- Призыв: написать в личку или позвонить"""
