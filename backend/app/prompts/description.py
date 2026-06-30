LANG_INSTRUCTIONS = {
    "ru": "Отвечай на русском языке.",
    "ua": "Відповідай українською мовою.",
    "en": "Reply in English.",
    "bg": "Отговаряй на български език.",
}


def build_prompt(params: dict, language: str) -> str:
    lang = LANG_INSTRUCTIONS.get(language, LANG_INSTRUCTIONS["ru"])
    features = ", ".join(params.get("features", [])) or "не указаны"

    return f"""{lang}
Ты профессиональный копирайтер для риелторов. Напиши продающее описание объекта недвижимости объёмом 150–250 слов.

Параметры объекта:
- Тип: {params.get("property_type", "")}
- Комнат: {params.get("rooms", "")}
- Этаж: {params.get("floor", "")} из {params.get("total_floors", "")}
- Общая площадь: {params.get("total_area", "")} м²
- Жилая площадь: {params.get("living_area", "")} м²
- Площадь кухни: {params.get("kitchen_area", "")} м²
- Район: {params.get("district", "")}
- Город: {params.get("city", "")}
- Состояние: {params.get("condition", "")}
- Особенности: {features}
- Дополнительно: {params.get("additional", "")}

Текст должен быть эмоциональным, убедительным и подчёркивать выгоды для покупателя. Не используй банальные фразы. Заканчивай призывом к действию."""
