LANG_INSTRUCTIONS = {
    "ru": "Отвечай на русском языке.",
    "ua": "Відповідай українською мовою.",
    "en": "Reply in English.",
    "bg": "Отговаряй на български език.",
}

OBJECTION_MAP = {
    "expensive": "«Дорого» — клиент считает цену завышенной",
    "think": "«Подумаю» — клиент откладывает решение",
    "comparing": "«Сравниваю варианты» — клиент смотрит конкурентов",
    "bad_location": "«Мне не нравится район» — возражение по локации",
    "discount": "«Хочу скидку» — клиент торгуется",
}


def build_prompt(params: dict, language: str) -> str:
    lang = LANG_INSTRUCTIONS.get(language, LANG_INSTRUCTIONS["ru"])
    objection_key = params.get("objection", "")
    objection_text = OBJECTION_MAP.get(objection_key, params.get("custom_objection", objection_key))

    return f"""{lang}
Ты тренер по продажам для риелторов. Дай 2-3 варианта профессионального ответа на возражение клиента.

Возражение: {objection_text}

Требования:
- Каждый вариант нумеруй
- Начинай с присоединения (понимаю, согласен, etc.)
- Затем переформулируй возражение или задай уточняющий вопрос
- Заканчивай переводом в следующий шаг
- Тон уверенный, не оправдывательный
- Каждый вариант — отдельный стиль (мягкий, прямой, вопросом)"""
