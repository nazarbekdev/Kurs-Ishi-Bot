from aiogram import Router, F
from aiogram.types import Message

qollanma_router = Router()


@qollanma_router.message(F.text == "📘 Qo'llanma")
async def guide_handler(message: Message):
    await message.answer(
        "<b>📘 Botdan foydalanish qo‘llanmasi</b>\n\n"
        "Quyidagi komandalar orqali kerakli xizmatlardan foydalanishingiz mumkin:\n\n"

        "🎓 <b>Kurs ishi yozish</b>\n"
        "└ /kurs_ishi yoki «Kurs ishi» tugmasi\n\n"

        "📄 <b>Mustaqil ish yozish</b>\n"
        "└ /mustaqil_ish yoki «Mustaqil ish» tugmasi\n\n"

        "📹 <b>Kurs ishi tayyorlash bo'yicha video</b>\n"
        "└ /video\n\n"
        
        "🔖 <b>Tariflarni ko‘rish</b>\n"
        "└ /tariflar yoki «Tariflar» tugmasi\n\n"

        "🎲 <b>Chegirma kuponi olish</b>\n"
        "└ /get_coupon yoki «Sirli Kupon» tugmasi\n\n"

        "💰 <b>Balansni tekshirish</b>\n"
        "└ /balans yoki «Balans» tugmasi\n\n"


        "👨‍💼 <b>Admin bilan bog‘lanish</b>\n"
        "└ /admin yoki to‘g‘ridan-to‘g‘ri 👉 @camtest_admin\n\n"

        "📎 <b>Namuna ishlar</b>: @kursishinamuna",
        parse_mode="HTML"
    )
