from openai import OpenAI
from dotenv import load_dotenv
from mundarija import generate_mundarija
from kirish import generate_kirish
from asosiy import generate_asosiy
from xulosa import generate_xulosa
from adabiyotlar import generate_foydalanilgan_adabiyotlar
from utils import merge_docs
import os


def generate_mustaqil_ish(fan_nomi: str, mavzu: str, til: str = "o'zbek tili", total_pages: int = 20) -> str:
    # OpenAI mijozini boshlash
    load_dotenv()
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # 1. Mundarija generatsiya qilish
    mundarija_path, reja_items = generate_mundarija(fan_nomi, mavzu, til, client)

    # 2. Kirish generatsiya qilish
    kirish_path = generate_kirish(fan_nomi, mavzu, til, client)

    # 3. Asosiy qism generatsiya qilish
    asosiy_path = generate_asosiy(fan_nomi, mavzu, til, reja_items, client, total_pages)

    # 4. Xulosa generatsiya qilish
    xulosa_path = generate_xulosa(fan_nomi, mavzu, til, client)

    # 5. Foydalanilgan adabiyotlar generatsiya qilish
    adabiyotlar_path = generate_foydalanilgan_adabiyotlar(fan_nomi, mavzu, til, total_pages, reja_items, client)

    # 6. Barcha bo‘limlarni birlashtirish
    file_paths = [mundarija_path, kirish_path, asosiy_path, xulosa_path, adabiyotlar_path]
    output_path = f"generated_docs/mustaqil_ish_{fan_nomi.lower().replace(' ', '_')}_{mavzu.lower().replace(' ', '_')}.docx"
    merge_docs(output_path, file_paths)

    return output_path


if __name__ == "__main__":
    fan_nomi = "English"
    mavzu = "Analysis of English and Uzbek poetry"
    til = "ingliz tili"
    total_pages = 8
    try:
        final_path = generate_mustaqil_ish(fan_nomi, mavzu, til, total_pages)
        print(f"Mustaqil ish muvaffaqiyatli yaratildi: {final_path}")
    except Exception as e:
        print(f"Xatolik yuz berdi: {str(e)}")
