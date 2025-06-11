from aiogram import Router, F
from aiogram.types import Message

router = Router()


@router.message(F.text.in_({"🔖 Tariflar", "/tariflar"}))
async def tariffs(message: Message):
    await message.answer(
        "📋 <b>Tariflar Ro‘yxati</b>\n\n"
        "📚 <b>Kurs Ishi</b>\n"
        "▫️ 10–20 sahifa: <code>30,000</code> so‘m\n"
        "▫️ 20–30 sahifa: <code>50,000</code> so‘m\n"
        "▫️ 30–40 sahifa: <code>70,000</code> so‘m\n\n"
        "📖 <b>Mustaqil Ish</b>\n"
        "▫️ Har bir ish: <code>7,000</code> so‘m\n\n"
        "💼 <b>Namunalar bilan tanishish</b>\n"
        "🔎 @kursishinamuna — bu bot orqali kurs ishi va mustaqil ishlarning <i>maxsus standart asosida yozilgan namunalarini</i> ko‘rishingiz mumkin.\n\n"
        "ℹ️ <b>Qo‘shimcha xizmatlar</b>\n"
        "👉 @camtest_admin bilan bog‘laning",
        parse_mode="HTML",
        disable_web_page_preview=True
    )
