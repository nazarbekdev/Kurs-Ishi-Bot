from openai import OpenAI
from docx import Document
from mustaqil_ish_utils.utils import add_formatted_paragraph
import os
import re

# "Xulosa" sarlavhasini tilga moslashtirish uchun lug‘at
CONCLUSION_TITLES = {
    "o'zbek tili": "Xulosa",
    "rus tili": "Заключение",
    "ingliz tili": "Conclusion"
}

# Prompt uchun tilga mos shablonlar
PROMPT_TEMPLATES = {
    "o'zbek tili": {
        "conclusion": "Xulosa",
        "prompt": lambda fan_nomi, mavzu: (
            f"'{fan_nomi}' fanidan '{mavzu}' mavzusida mustaqil ish uchun 'Xulosa' bo‘limini yozing. "
            "Matn 150-200 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. "
            f"'Xulosa' deb boshlama!!! "
            "Bo‘limda asosiy topilmalar va takliflar haqida yozing."
        )
    },
    "rus tili": {
        "conclusion": "Заключение",
        "prompt": lambda fan_nomi, mavzu: (
            f"Напишите раздел 'Заключение' для самостоятельной работы по дисциплине '{fan_nomi}' на тему '{mavzu}'. "
            "Текст должен состоять из 150-200 слов, на русском языке, в научном стиле, без плагиата. "
            f"Не начинайте текст с 'Заключение'!!! "
            "В разделе опишите основные выводы и предложения."
        )
    },
    "ingliz tili": {
        "conclusion": "Conclusion",
        "prompt": lambda fan_nomi, mavzu: (
            f"Write the 'Conclusion' section for an independent study in the field of '{fan_nomi}' on the topic '{mavzu}'. "
            "The text should be 150-200 words, in English, in a scientific style, free of plagiarism. "
            f"Do not start the text with 'Conclusion'!!! "
            "In the section, describe the main findings and suggestions."
        )
    }
}


def sanitize_filename(filename: str) -> str:
    """Fayl nomini maxsus belgilardan tozalash."""
    return re.sub(r'[^\w\s-]', '', filename).strip().replace(' ', '_')


def generate_xulosa(fan_nomi: str, mavzu: str, til: str) -> str:
    """
    Xulosa bo‘limini generatsiya qilish va DOCX fayl sifatida saqlash.

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
    conclusion_title = CONCLUSION_TITLES.get(til.lower(), "Xulosa")
    add_formatted_paragraph(document, conclusion_title, is_heading=True, is_bold=True)

    # Xulosa matnini generatsiya qilish
    prompt = template["prompt"](fan_nomi, mavzu)
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        xulosa_text = response.choices[0].message.content.strip()
        print(f"Generatsiya qilingan xulosa: {xulosa_text[:200]}...")
    except Exception as e:
        print(f"OpenAI xatosi (Xulosa): {str(e)}")
        xulosa_text = f"{conclusion_title} bo‘limi hozircha mavjud emas."

    # Matnni qo‘shish
    for line in xulosa_text.split('\n'):
        if line.strip():
            add_formatted_paragraph(document, line, is_bold=False)

    # Faylni saqlash
    try:
        sanitized_mavzu = sanitize_filename(mavzu)
        save_path = f"generated_docs/xulosa_{sanitized_mavzu}_{til.lower().replace(' ', '_')}.docx"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        document.save(save_path)
        print(f"Xulosa fayli saqlandi: {save_path}")
    except Exception as e:
        raise Exception(f"Fayl saqlashda xato: {str(e)}")

    return save_path


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    fan_nomi = "Pedagogika"
    mavzu = "MAKTABGACHA TA’LIM MUASSASASI, OILA VA MAKTAB HAMKORLIGI"
    til = "o'zbek tili"
    save_path = generate_xulosa(fan_nomi, mavzu, til)
