LANGUAGE_NAMES = {
    "ru": "русском",
    "ua": "украинском",
    "en": "English",
    "bg": "болгарском",
}

PROPERTY_TYPE_NAMES = {
    "ru": {
        "apartment": "квартиры",
        "house": "дома",
        "commercial": "коммерческого помещения",
    },
    "ua": {
        "apartment": "квартири",
        "house": "будинку",
        "commercial": "комерційного приміщення",
    },
    "en": {
        "apartment": "apartment",
        "house": "house",
        "commercial": "commercial property",
    },
    "bg": {
        "apartment": "апартамент",
        "house": "къща",
        "commercial": "търговски имот",
    },
}


def build_prompt(property_type: str, language: str, additional: str = "") -> str:
    lang_name = LANGUAGE_NAMES.get(language, "русском")
    prop_names = PROPERTY_TYPE_NAMES.get(language, PROPERTY_TYPE_NAMES["ru"])
    prop_name = prop_names.get(property_type, prop_names["apartment"])

    additional_block = f"\nДополнительная информация от риелтора: {additional}" if additional.strip() else ""

    if language == "en":
        return (
            f"You are a professional real estate agent and copywriter. "
            f"Analyze this photo of a {prop_name} and write a compelling property description in English, "
            f"150–250 words.\n"
            f"Describe what you see: the condition of the renovation, layout impression, special features, "
            f"atmosphere, natural light, and any standout details that would attract buyers.\n"
            f"Write in a warm, professional, sales-oriented tone. Focus on benefits, not just features.\n"
            f"{additional_block}"
        )
    else:
        return (
            f"Ты профессиональный риелтор и копирайтер. "
            f"Проанализируй фото {prop_name} и составь продающее описание на {lang_name} языке, 150–250 слов.\n"
            f"Опиши что видишь: состояние ремонта, впечатление от планировки, особенности, атмосферу, "
            f"естественное освещение и любые детали, которые привлекут покупателей.\n"
            f"Пиши тепло, профессионально, с продающим акцентом. Фокус на преимуществах, а не просто на фактах.\n"
            f"{additional_block}"
        )
