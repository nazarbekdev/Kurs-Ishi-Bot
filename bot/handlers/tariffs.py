from aiogram import Router, F
from aiogram.types import Message

router = Router()


@router.message(F.text == "🔖 Tariflar")
async def tariffs(message: Message):
    await message.answer(
        "📋 <b>Tariflar Ro‘yxati</b>\n\n"
        "📚 <b>Kurs Ishi</b>\n"
        "- 10-20 sahifa: <code>30,000</code> so‘m\n"
        "- 20-30 sahifa: <code>50,000</code> so‘m\n"
        "- 30-40 sahifa: <code>70,000</code> so‘m\n\n"
        "📖 <b>Mustaqil Ish</b>\n"
        "- Har bir ish: <code>7,000</code> so‘m\n\n\n"
        "ℹ️ <b>Qo'shimcha Xizmatlar:</b>\n"
        "👉 @camtest_admin bilan bog‘laning",
        parse_mode="HTML"
    )
