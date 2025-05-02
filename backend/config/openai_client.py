from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_coursework(field, topic, university, pages, language):
    prompt = f"""
    Siz O‘zbekiston universitetlari uchun ilmiy kurs ishi yozadigan yuqori malakali sun’iy intellektsiz.

    Quyidagi ma’lumotlarga asoslanib {pages} sahifali ilmiy kurs ishi tayyorlang:
    - Soha: {field}
    - Mavzu: {topic}
    - Universitet: {university}
    - Til: {language}

    Kurs ishi **O‘zbekiston ta’lim standartlariga mos** va **ilmiy** uslubda yozilsin.

    **Tuzilishi quyidagicha bo‘lsin:**

    1. **Kirish**:  
       - Mavzuning dolzarbligi, ahamiyati va ilmiy yangiligi.  
       - Tadqiqotning maqsad va vazifalari.  
       - Tadqiqotning predmeti va ob’ekti.  
       - Tadqiqot metodlari va ishlash usullari.  
       - Kurs ishining umumiy tuzilmasi haqida qisqacha.

    2. **Asosiy qism**:  
       - **I bo‘lim: Nazariy tahlil**  
         - Mavzu bo‘yicha adabiyotlar tahlili (kamida 3 ta manba).
         - Asosiy nazariy yondashuvlar va ilmiy qarashlar.  
       - **II bo‘lim: Amaliy qism**  
         - Tadqiqot metodikasi, o‘rganilgan ma’lumotlar va natijalar.  
         - Jadval, kod misollar, matematik formulalar, grafik va diagrammalar keltiring (lozim bo‘lsa).  
       - **III bo‘lim: Takliflar va xulosalar**  
         - Amaliy natijalar asosida tavsiyalar.  
         - Kelgusidagi ilmiy izlanishlar uchun yo‘nalishlar.

    3. **Xulosa**:  
       - Tadqiqot yakunlari, ilmiy va amaliy natijalari.  
       - Qo‘yilgan maqsad va vazifalarning bajarilishi haqida xulosa.

    4. **Foydalanilgan adabiyotlar ro‘yxati**:  
       - Kamida 10 ta manba: GOST 7.1-2003 talabiga mos shaklda. (me’yoriy hujjatlar, ilmiy maqolalar va darsliklar)

    **Qo‘shimcha talablari:**
    - Har bir bo‘lim sarlavha bilan aniq ajratilsin.
    - Matn rasmiy va ilmiy uslubda bo‘lsin.
    - Zarur joylarda kodlar, matematik formulalar yoki jadval ko‘rinishida misollar keltirilsin.
    - Kod bloklari alohida blok ko‘rinishida bo‘lsin (```) belgilar ichida yozilsin).
    - Matematik formulalar (masalan, integral, logarifm) latex ko‘rinishida yozilsin ($$ belgilari bilan).
    - Jadval bo‘lsa, markdown jadval shaklida keltiring.

    Kurs ishi sifatli, mantiqiy bog‘langan, o‘quvchiga tushunarli va professional bo‘lishi shart.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Siz ilmiy kurs ishlari yozishga ixtisoslashgan AI modelisiz."},
            {"role": "user", "content": prompt}
        ]
    )
    print('Kurs ishi:', response.choices[0].message.content)
    return response.choices[0].message.content
