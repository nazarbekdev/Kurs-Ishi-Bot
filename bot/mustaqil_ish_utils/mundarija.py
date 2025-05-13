from openai import OpenAI
from docx import Document
from mustaqil_ish_utils.utils import add_formatted_paragraph
import os
import re

# Tilga mos sarlavhalar uchun lug‘atlar
CONTENT_TITLES = {
    "o'zbek tili": {
        "reja": "Reja:",
        "kirish": "Kirish",
        "xulosa": "Xulosa",
        "foydalanilgan_adabiyotlar": "Foydalanilgan adabiyotlar"
    },
    "rus tili": {
        "reja": "План:",
        "kirish": "Введение",
        "xulosa": "Заключение",
        "foydalanilgan_adabiyotlar": "Список литературы"
    },
    "ingliz tili": {
        "reja": "Contents:",
        "kirish": "Introduction",
        "xulosa": "Conclusion",
        "foydalanilgan_adabiyotlar": "References"
    }
}

# Prompt uchun tilga mos shablonlar
PROMPT_TEMPLATES = {
    "o'zbek tili": {
        "prompt": lambda fan_nomi, mavzu: (
            f"'{fan_nomi}' fanidan '{mavzu}' mavzusida mustaqil ish uchun 5 ta banddan iborat reja tuzing. "
            "Har bir band 1-2 jumlali qisqa sarlavha bo‘lsin, O‘zbek tilida, ilmiy uslubda. "
            "Faqat bandlarni ro‘yxat sifatida qaytaring, qo‘shimcha tushuntirishsiz."
        )
    },
    "rus tili": {
        "prompt": lambda fan_nomi, mavzu: (
            f"Составьте план из 5 пунктов для самостоятельной работы по дисциплине '{fan_nomi}' на тему '{mavzu}'. "
            "Каждый пункт должен быть коротким заголовком из 1-2 предложений, на русском языке, в научном стиле. "
            "Возвращайте только пункты в виде списка, без дополнительных пояснений."
        )
    },
    "ingliz tili": {
        "prompt": lambda fan_nomi, mavzu: (
            f"Create a plan with 5 items for an independent study in the field of '{fan_nomi}' on the topic '{mavzu}'. "
            "Each item should be a short heading of 1-2 sentences, in English, in a scientific style. "
            "Return only the items as a list, without additional explanations."
        )
    }
}


def sanitize_filename(filename: str) -> str:
    """Fayl nomini maxsus belgilardan tozalash."""
    return re.sub(r'[^\w\s-]', '', filename).strip().replace(' ', '_')


def generate_mundarija(fan_nomi: str, mavzu: str, til: str) -> tuple[str, list]:
    """
    Mundarija bo‘limini generatsiya qilish va DOCX fayl sifatida saqlash.

    Args:
        fan_nomi (str): Fanning nomi.
        mavzu (str): Mustaqil ish mavzusi.
        til (str): Til ("o'zbek tili", "rus tili", "ingliz tili").

    Returns:
        tuple[str, list]: Saqlangan DOCX fayl yo'li va reja bandlari ro‘yxati.
    """
    document = Document()
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # Tilga mos shablonni olish
    titles = CONTENT_TITLES.get(til.lower(), CONTENT_TITLES["o'zbek tili"])  # Default: O‘zbek tili
    template = PROMPT_TEMPLATES.get(til.lower(), PROMPT_TEMPLATES["o'zbek tili"])  # Default: O‘zbek tili

    # Mavzu nomini katta harflar bilan markazga qo‘shish
    add_formatted_paragraph(document, mavzu.upper(), is_heading=True, is_center=True, is_bold=True)

    # "Reja:" qo‘shish (tilga mos)
    add_formatted_paragraph(document, titles["reja"], is_heading=True, is_bold=True)

    # "Kirish" qo‘shish (tilga mos)
    add_formatted_paragraph(document, titles["kirish"], is_heading=True, is_bold=True)

    # OpenAI orqali 5 ta bandli reja generatsiya qilish
    prompt = template["prompt"](fan_nomi, mavzu)
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        reja_items = response.choices[0].message.content.strip().split('\n')
        reja_items = [item.strip() for item in reja_items if item.strip()]
        print(f"Generatsiya qilingan reja: {reja_items}")
    except Exception as e:
        print(f"OpenAI xatosi (Reja): {str(e)}")
        reja_items = [
            f"1. {titles['kirish']} 1.",
            "2. Section 2.",
            "3. Section 3.",
            "4. Section 4.",
            "5. Section 5."
        ]

    # 5 ta bandni qo‘shish
    for idx, item in enumerate(reja_items[:5], 1):
        # Agar band raqam bilan boshlanmasa, qo‘shib yozamiz
        if not item.startswith(f"{idx}."):
            item = f"{idx}. {item}"
        add_formatted_paragraph(document, item, is_bold=False)

    # "Xulosa" qo‘shish (tilga mos)
    add_formatted_paragraph(document, titles["xulosa"], is_heading=True, is_bold=True)

    # "Foydalanilgan adabiyotlar" qo‘shish (tilga mos)
    add_formatted_paragraph(document, titles["foydalanilgan_adabiyotlar"], is_heading=True, is_bold=True)

    # Faylni saqlash
    try:
        sanitized_mavzu = sanitize_filename(mavzu)
        save_path = f"generated_docs/mundarija_{sanitized_mavzu}_{til.lower().replace(' ', '_')}.docx"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        document.save(save_path)
        print(f"Mundarija fayli saqlandi: {save_path}")
    except Exception as e:
        raise Exception(f"Fayl saqlashda xato: {str(e)}")

    return save_path, reja_items[:5]


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    fan_nomi = "Pedagogika"
    mavzu = "MAKTABGACHA TA’LIM MUASSASASI, OILA VA MAKTAB HAMKORLIGI"
    til = "o'zbek tili"
    save_path, reja = generate_mundarija(fan_nomi, mavzu, til)
    print(f"Saqlangan reja: {reja}")
