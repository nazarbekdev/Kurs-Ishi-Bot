from openai import OpenAI
from docx import Document
from mustaqil_ish_utils.utils import add_formatted_paragraph
import os
import re

# "Kirish" sarlavhasini tilga moslashtirish uchun lug‘at
INTRODUCTION_TITLES = {
    "o'zbek tili": "Kirish",
    "rus tili": "Введение",
    "ingliz tili": "Introduction"
}

# Prompt uchun tilga mos shablonlar
PROMPT_TEMPLATES = {
    "o'zbek tili": {
        "introduction": "Kirish",
        "prompt": lambda fan_nomi, mavzu: (
            f"'{fan_nomi}' fanidan '{mavzu}' mavzusida mustaqil ish uchun 'Kirish' bo‘limini yozing. "
            "Matn 200-300 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. "
            f"'Kirish' so'zi bilan boshlamang!!! "
            "Bo‘limda mavzuning dolzarbligi, ahamiyati va umumiy maqsadlari haqida yozing."
        )
    },
    "rus tili": {
        "introduction": "Введение",
        "prompt": lambda fan_nomi, mavzu: (
            f"Напишите раздел 'Введение' для самостоятельной работы по дисциплине '{fan_nomi}' на тему '{mavzu}'. "
            "Текст должен состоять из 200-300 слов, на русском языке, в научном стиле, без плагиата. "
            f"Не начинайте текст с 'Введение'!!! "
            "В разделе опишите актуальность темы, её значимость и общие цели."
        )
    },
    "ingliz tili": {
        "introduction": "Introduction",
        "prompt": lambda fan_nomi, mavzu: (
            f"Write the 'Introduction' section for an independent study in the field of '{fan_nomi}' on the topic '{mavzu}'. "
            "The text should be 200-300 words, in English, in a scientific style, free of plagiarism. "
            f"Do not start the text with 'Introduction'!!! "
            "In the section, describe the relevance of the topic, its importance, and the general objectives."
        )
    }
}


def sanitize_filename(filename: str) -> str:
    """Fayl nomini maxsus belgilardan tozalash."""
    return re.sub(r'[^\w\s-]', '', filename).strip().replace(' ', '_')


def generate_kirish(fan_nomi: str, mavzu: str, til: str) -> str:
    """
    Kirish bo‘limini generatsiya qilish va DOCX fayl sifatida saqlash.

    Args:
        fan_nomi (str): Fanning nomi.
        mavzu (str): Mustaqil ish mavzusi.
        til (str): Til ("o'zbek tili", "rus tili", "ingliz tili").
        client (OpenAI): OpenAI mijoz obyekti.

    Returns:
        str: Saqlangan DOCX fayl yo'li.
    """
    document = Document()
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # Tilga mos shablonni olish
    template = PROMPT_TEMPLATES.get(til.lower(), PROMPT_TEMPLATES["o'zbek tili"])  # Default: O‘zbek tili

    # Sarlavha qo‘shish (tilga mos)
    introduction_title = INTRODUCTION_TITLES.get(til.lower(), "Kirish")
    add_formatted_paragraph(document, introduction_title, is_heading=True, is_bold=True)

    # Kirish matnini generatsiya qilish
    prompt = template["prompt"](fan_nomi, mavzu)
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        kirish_text = response.choices[0].message.content.strip()
        print(f"Generatsiya qilingan kirish: {kirish_text[:200]}...")
    except Exception as e:
        print(f"OpenAI xatosi (Kirish): {str(e)}")
        kirish_text = f"{introduction_title} bo‘limi hozircha mavjud emas."

    # Matnni qo‘shish
    for line in kirish_text.split('\n'):
        if line.strip():
            add_formatted_paragraph(document, line, is_bold=False)

    # Faylni saqlash
    try:
        sanitized_mavzu = sanitize_filename(mavzu)
        save_path = f"generated_docs/kirish_{sanitized_mavzu}_{til.lower().replace(' ', '_')}.docx"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        document.save(save_path)
        print(f"Kirish fayli saqlandi: {save_path}")
    except Exception as e:
        raise Exception(f"Fayl saqlashda xato: {str(e)}")

    return save_path


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    fan_nomi = "Pedagogika"
    mavzu = "MAKTABGACHA TA’LIM MUASSASASI, OILA VA MAKTAB HAMKORLIGI"
    til = "o'zbek tili"
    save_path = generate_kirish(fan_nomi, mavzu, til)
