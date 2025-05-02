from openai import OpenAI
from dotenv import load_dotenv
import os

# Atrof-muhit o‘zgaruvchilarini yuklash
load_dotenv()

# OpenAI mijozini boshlash
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Prompt shablonlari
PROMPT_TEMPLATES = {
    "Tibbiyot": {
        "o'zbek tili": {
            "chapter_1": {
                "chapter_title": "I. BOB. TIBBIYOT SOHASIDA {mavzu} NING NAZARIY ASOSLARI",
                "sections": [
                    {"title": "1.1. {mavzu} bo‘yicha asosiy tushunchalar va ilmiy nazariy asoslar",
                     "prompt": "{mavzu} bo‘yicha asosiy tushunchalar va ilmiy nazariy asoslar haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Hech qanday Kirish va Xulosa qismlari bo'lmasin! Klinik ma'lumotlarni keltir. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va ilmiy tahlillarni qo‘sh."},
                    {"title": "1.2. {mavzu} ga ta’sir etuvchi omillar",
                     "prompt": "{mavzu} ga ta’sir etuvchi omillar haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Hech qanday Kirish va Xulosa qismlari bo'lmasin! Fiziologik va patologik omillarni tahlil qil, jadvallar qo‘sh. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va ilmiy tahlillarni qo‘sh."},
                    {"title": "1.3. {mavzu} bo‘yicha zamonaviy tadqiqotlar va ularning natijalari",
                     "prompt": "{mavzu} bo‘yicha zamonaviy tadqiqotlar va ularning natijalari haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Hech qanday Kirish va Xulosa qismlari bo'lmasin! Ilmiy tahlillarni keltir. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va ilmiy tahlillarni qo‘sh."}
                ]
            },
            "chapter_2": {
                "chapter_title": "II. BOB. TIBBIYOT SOHASIDA {mavzu} NING AMALIY TAHLILI",
                "sections": [
                    {"title": "2.1. Tadqiqot metodologiyasi",
                     "prompt": "Tibbiyot sohasida {mavzu} bo‘yicha tadqiqot metodologiyasi haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Klinik tadqiqot usullarini tahlil qil. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va ilmiy tahlillarni qo‘sh."},
                    {"title": "2.2. Tadqiqot natijalari",
                     "prompt": "Tibbiyot sohasida {mavzu} bo‘yicha tadqiqot natijalari haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Jadvallar va statistik ma'lumotlar bilan tahlil qil. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va ilmiy tahlillarni qo‘sh."},
                    {"title": "2.3. Amaliy takliflar",
                     "prompt": "Tibbiyot sohasida {mavzu} bo‘yicha amaliy takliflar haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Tibbiyot amaliyotida qo‘llash bo‘yicha takliflar keltir. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va ilmiy tahlillarni qo‘sh."}
                ]
            }
        }
    },
    "IT": {
        "o'zbek tili": {
            "chapter_1": {
                "chapter_title": "I. BOB. AXBOROT TEXNOLOGIYALARI SOHASIDA {mavzu} NING NAZARIY ASOSLARI",
                "sections": [
                    {"title": "1.1. {mavzu} bo‘yicha asosiy tushunchalar va texnologik asoslar",
                     "prompt": "{mavzu} bo‘yicha asosiy tushunchalar va texnologik asoslar haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Hech qanday Kirish va Xulosa qismlari bo'lmasin! Dasturiy ta'minotlarni tahlil qil. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va ilmiy tahlillarni qo‘sh."},
                    {"title": "1.2. {mavzu} ga ta’sir etuvchi omillar",
                     "prompt": "{mavzu} ga ta’sir etuvchi omillar haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Hech qanday Kirish va Xulosa qismlari bo'lmasin! Texnologik va iqtisodiy omillarni keltir, jadvallar qo‘sh. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va ilmiy tahlillarni qo‘sh."},
                    {"title": "1.3. {mavzu} bo‘yicha qo‘llaniladigan texnologiyalar",
                     "prompt": "{mavzu} bo‘yicha qo‘llaniladigan texnologiyalar haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Hech qanday Kirish va Xulosa qismlari bo'lmasin! Kod misollari bilan (masalan, Python yoki Java). Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va kod misollarini (``` bilan) qo‘sh."}
                ]
            },
            "chapter_2": {
                "chapter_title": "II. BOB. AXBOROT TEXNOLOGIYALARI SOHASIDA {mavzu} NING AMALIY TAHLILI",
                "sections": [
                    {"title": "2.1. Tadqiqot metodologiyasi",
                     "prompt": "Axborot Texnologiyalari sohasida {mavzu} bo‘yicha tadqiqot metodologiyasi haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Dasturiy loyiha metodlarini tahlil qil. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va ilmiy tahlillarni qo‘sh."},
                    {"title": "2.2. Amaliy natijalar",
                     "prompt": "Axborot Texnologiyalari sohasida {mavzu} bo‘yicha amaliy natijalar haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Kod misollari va statistik ma'lumotlar bilan tahlil qil. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va kod misollarini (``` bilan) qo‘sh."},
                    {"title": "2.3. Amaliy takliflar",
                     "prompt": "Axborot Texnologiyalari sohasida {mavzu} bo‘yicha amaliy takliflar haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. IT sohasida qo‘llash bo‘yicha takliflar keltir. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va ilmiy tahlillarni qo‘sh."}
                ]
            }
        }
    },
    "Iqtisodiyot": {
        "o'zbek tili": {
            "chapter_1": {
                "chapter_title": "I. BOB. IQTISODIYOT SOHASIDA {mavzu} NING NAZARIY ASOSLARI",
                "sections": [
                    {"title": "1.1. {mavzu} bo‘yicha asosiy tushunchalar va nazariy asoslar",
                     "prompt": "{mavzu} bo‘yicha asosiy tushunchalar va nazariy asoslar haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Hech qanday Kirish va Xulosa qismlari bo'lmasin! Iqtisodiy modellarni keltir. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va ilmiy tahlillarni qo‘sh."},
                    {"title": "1.2. {mavzu} ga ta’sir etuvchi omillar",
                     "prompt": "{mavzu} ga ta’sir etuvchi omillar haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Hech qanday Kirish va Xulosa qismlari bo'lmasin! Iqtisodiy omillarni tahlil qil, jadvallar qo‘sh. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va ilmiy tahlillarni qo‘sh."},
                    {"title": "1.3. {mavzu} bo‘yicha zamonaviy iqtisodiy yondashuvlar",
                     "prompt": "{mavzu} bo‘yicha zamonaviy iqtisodiy yondashuvlar haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Hech qanday Kirish va Xulosa qismlari bo'lmasin! Statistik ma'lumotlar va prognozlar bilan. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va iqtisodiy tahlillarni qo‘sh."}
                ]
            },
            "chapter_2": {
                "chapter_title": "II. BOB. IQTISODIYOT SOHASIDA {mavzu} NING AMALIY TAHLILI",
                "sections": [
                    {"title": "2.1. Tadqiqot metodologiyasi",
                     "prompt": "Iqtisodiyot sohasida {mavzu} bo‘yicha tadqiqot metodologiyasi haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Iqtisodiy tahlil usullarini keltir. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va ilmiy tahlillarni qo‘sh."},
                    {"title": "2.2. Tadqiqot natijalari",
                     "prompt": "Iqtisodiyot sohasida {mavzu} bo‘yicha tadqiqot natijalari haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Jadvallar, grafiklar va statistik ma'lumotlar bilan tahlil qil. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va iqtisodiy tahlillarni qo‘sh."},
                    {"title": "2.3. Amaliy takliflar",
                     "prompt": "Iqtisodiyot sohasida {mavzu} bo‘yicha am şansiy takliflar haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Iqtisodiy strategiyalar bo‘yicha takliflar keltir. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va iqtisodiy tahlillarni qo‘sh."}
                ]
            }
        }
    },
    "Matematika": {
        "o'zbek tili": {
            "chapter_1": {
                "chapter_title": "I. BOB. MATEMATIKA SOHASIDA {mavzu} NING NAZARIY ASOSLARI",
                "sections": [
                    {"title": "1.1. {mavzu} bo‘yicha asosiy tushunchalar va nazariy asoslar",
                     "prompt": "{mavzu} bo‘yicha asosiy tushunchalar va nazariy asoslar haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Hech qanday Kirish va Xulosa qismlari bo'lmasin! Ilmiy dalillarni keltir. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va matematik tahlillarni qo‘sh."},
                    {"title": "1.2. {mavzu} bo‘yicha matematik modellar va isbotlar",
                     "prompt": "{mavzu} bo‘yicha matematik modellar va isbotlar haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Hech qanday Kirish va Xulosa qismlari bo'lmasin! Misollar bilan tahlil qil. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va matematik tahlillarni qo‘sh."},
                    {"title": "1.3. {mavzu} bo‘yicha qo‘llaniladigan usullar",
                     "prompt": "{mavzu} bo‘yicha qo‘llaniladigan usullar haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Hech qanday Kirish va Xulosa qismlari bo'lmasin! Jadvallar va grafiklar bilan tahlil qil. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va matematik tahlillarni qo‘sh."}
                ]
            },
            "chapter_2": {
                "chapter_title": "II. BOB. MATEMATIKA SOHASIDA {mavzu} NING AMALIY TAHLILI",
                "sections": [
                    {"title": "2.1. Tadqiqot metodologiyasi",
                     "prompt": "Matematika sohasida {mavzu} bo‘yicha tadqiqot metodologiyasi haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Matematik tahlil usullarini keltir. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va matematik tahlillarni qo‘sh."},
                    {"title": "2.2. Tadqiqot natijalari",
                     "prompt": "Matematika sohasida {mavzu} bo‘yicha tadqiqot natijalari haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Misollar, isbotlar va jadvallar bilan tahlil qil. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va matematik tahlillarni qo‘sh."},
                    {"title": "2.3. Amaliy qo‘llanmalar",
                     "prompt": "Matematika sohasida {mavzu} bo‘yicha amaliy qo‘llanmalar haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Matematik modellarni qo‘llash bo‘yicha takliflar keltir. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va matematik tahlillarni qo‘sh."}
                ]
            }
        }
    },
    "Umumiy": {
        "o'zbek tili": {
            "chapter_1": {
                "chapter_title": "I. BOB. {fan_nomi} SOHASIDA {mavzu} NING NAZARIY ASOSLARI",
                "sections": [
                    {"title": "1.1. {mavzu} bo‘yicha asosiy tushunchalar va nazariy asoslar",
                     "prompt": "{mavzu} bo‘yicha asosiy tushunchalar va nazariy asoslar haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Hech qanday Kirish va Xulosa qismlari bo'lmasin! Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va ilmiy tahlillarni qo‘sh."},
                    {"title": "1.2. {mavzu} ga ta’sir etuvchi omillar yoki jarayonlar",
                     "prompt": "{mavzu} ga ta’sir etuvchi omillar yoki jarayonlar haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Hech qanday Kirish va Xulosa qismlari bo'lmasin! Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va ilmiy tahlillarni qo‘sh."},
                    {"title": "1.3. {mavzu} bo‘yicha qo‘llaniladigan usullar yoki texnologiyalar",
                     "prompt": "{mavzu} bo‘yicha qo‘llaniladigan usullar yoki texnologiyalar haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Hech qanday Kirish va Xulosa qismlari bo'lmasin! Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va ilmiy tahlillarni qo‘sh."}
                ]
            },
            "chapter_2": {
                "chapter_title": "II. BOB. {fan_nomi} SOHASIDA {mavzu} NING AMALIY TAHLILI",
                "sections": [
                    {"title": "2.1. Tadqiqot metodologiyasi",
                     "prompt": "{fan_nomi} sohasida {mavzu} bo‘yicha tadqiqot metodologiyasi haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va ilmiy tahlillarni qo‘sh."},
                    {"title": "2.2. Tadqiqot natijalari",
                     "prompt": "{fan_nomi} sohasida {mavzu} bo‘yicha tadqiqot natijalari haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va ilmiy tahlillarni qo‘sh."},
                    {"title": "2.3. Amaliy takliflar",
                     "prompt": "{fan_nomi} sohasida {mavzu} bo‘yicha amaliy takliflar haqida ilmiy ma'lumot ber, 1000 so‘zdan iborat bo‘lsin, O‘zbek tilida, ilmiy uslubda, plagiatdan xoli bo‘lsin. Markdown formatida bo‘limlar (###), ro‘yxatlar (- yoki 1.), jadvallar (| bilan) va ilmiy tahlillarni qo‘sh."}
                ]
            }
        }
    }
}


def detect_field(fan_nomi: str, mavzu: str) -> str:
    """
    fan_nomi va mavzu asosida sohani aniqlash uchun OpenAI’dan foydalanamiz.

    Args:
        fan_nomi (str): Fanning nomi (masalan, "Tibbiyot", "Axborot texnologiyalari").
        mavzu (str): Kurs ishi mavzusi (masalan, "Yurak urishi va uni to'xtab qolish sabablari").

    Returns:
        str: Aniqlangan soha (masalan, "Tibbiyot", "IT", "Iqtisodiyot", "Matematika").
    """
    prompt = f"""
    Quyidagi fan nomi va mavzuga asoslanib, bu kurs ishi qaysi soha (Tibbiyot, IT, Iqtisodiyot, Matematika yoki boshqa) ga tegishli ekanligini aniqlang. Faqat soha nomini qaytaring, qo‘shimcha izoh bermasdan.

    Fan nomi: {fan_nomi}
    Mavzu: {mavzu}

    Masalan: "Tibbiyot", "IT", "Iqtisodiyot", "Matematika"
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=50
        )
        field = response.choices[0].message.content.strip()
        return field
    except Exception as e:
        print(f"Soha aniqlashda xato: {str(e)}")
        return "Umumiy"  # Agar xato bo‘lsa, umumiy shablon ishlatiladi


def generate_prompt_template(fan_nomi: str, mavzu: str, til: str, chapter: str) -> dict:
    """
    fan_nomi va mavzu asosida mos prompt shablonini generatsiya qilish.

    Args:
        fan_nomi (str): Fanning nomi.
        mavzu (str): Kurs ishi mavzusi.
        til (str): Til ("o'zbek tili", "rus tili", "ingliz tili").
        chapter (str): Bob turi ("chapter_1" yoki "chapter_2").

    Returns:
        dict: Shablon (chapter_title va sections).
    """
    # Sohani aniqlash
    field = detect_field(fan_nomi, mavzu)
    print(f"Aniqlangan soha: {field}")

    # Agar soha shablonlar ro‘yxatida bo‘lmasa, umumiy shablonni ishlatamiz
    if field not in PROMPT_TEMPLATES:
        field = "Umumiy"

    # Shablonni olish
    template = PROMPT_TEMPLATES[field][til][chapter]

    # Shablonni dinamik qilish (fan_nomi va mavzu ni qo‘shish)
    formatted_template = {
        "chapter_title": template["chapter_title"].format(fan_nomi=fan_nomi, mavzu=mavzu),
        "sections": [
            {
                "title": section["title"].format(mavzu=mavzu),
                "prompt": section["prompt"].format(fan_nomi=fan_nomi, mavzu=mavzu)
            }
            for section in template["sections"]
        ]
    }

    return formatted_template


# Test qilish
if __name__ == "__main__":
    test_cases = [
        {"fan_nomi": "Tibbiyot", "mavzu": "Yurak urishi va uni to'xtab qolish sabablari", "til": "o'zbek tili"},
        {"fan_nomi": "Axborot texnologiyalari", "mavzu": "Sun’iy intellektning rivojlanishi", "til": "o'zbek tili"},
        {"fan_nomi": "Iqtisodiyot", "mavzu": "O‘zbekiston iqtisodiyotidagi inflyatsiya", "til": "o'zbek tili"},
        {"fan_nomi": "Matematika", "mavzu": "Funksiyalarning grafik tahlili", "til": "o'zbek tili"},
    ]

    for case in test_cases:
        fan_nomi = case["fan_nomi"]
        mavzu = case["mavzu"]
        til = case["til"]

        print(f"\nTest: {fan_nomi} - {mavzu} ({til})")

        # I Bob shablonini generatsiya qilish
        chapter_1_template = generate_prompt_template(fan_nomi, mavzu, til, "chapter_1")
        print("I Bob Shabloni:")
        print(f"Chapter Title: {chapter_1_template['chapter_title']}")
        for section in chapter_1_template["sections"]:
            print(f"Section: {section['title']}")
            print(f"Prompt: {section['prompt'][:100]}...")  # Promptni qisqa ko‘rsatish uchun

        # II Bob shablonini generatsiya qilish
        chapter_2_template = generate_prompt_template(fan_nomi, mavzu, til, "chapter_2")
        print("\nII Bob Shabloni:")
        print(f"Chapter Title: {chapter_2_template['chapter_title']}")
        for section in chapter_2_template["sections"]:
            print(f"Section: {section['title']}")
            print(f"Prompt: {section['prompt'][:100]}...")  # Promptni qisqa ko‘rsatish uchun
