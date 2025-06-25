from aiogram import Router, F
from aiogram.types import Message
from keyboards.keyboards import main_kb
from aiogram.enums import ParseMode
import aiohttp
import os

router = Router()

API_URL = os.getenv('API_URL')


@router.message(F.text == "/start")
async def start_handler(message: Message):
    await save_user(message)
    await message.answer(
        "👋 <b>Assalomu alaykum!</b>\n"
        "<b>Kurs Ishi Robot</b> ga xush kelibsiz! 🎓\n\n"
        "🎲 Har kuni <b>Sirli Kupon</b> orqali <b>20 %</b> gacha chegirmalardan foydalaning!\n"
        "👉 /get_coupon buyrug‘ini yozing.\n\n"
        "📹 Kurs ishi yozishni o‘rganish uchun:\n"
        "👉 /video buyrug‘ini yozing.",
        reply_markup=main_kb,
        parse_mode=ParseMode.HTML
    )


async def save_user(message: Message):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}/api/create/", json={
            "full_name": message.from_user.full_name,
            "telegram_id": message.from_user.id
        }) as resp:
            if resp.status == 201:
                print('User saved')


@router.message(F.text.in_({"👨‍💻 Admin", "/admin"}))
async def start_handler(message: Message):
    await message.answer(
        "📞 <b>Admin bilan aloqa</b>\n"
        "──────────────────────\n"
        "📬 <b>Taklif yoki savollar</b> bo‘yicha:\n"
        "🔗 @camtest_admin\n\n"
        "👨‍💻 <b>Bot dasturchisi:</b>\n"
        "🔗 @happiness_0405\n\n"
        "📞 <b>Bog'lanish uchun:</b>\n"
        "🔗 +998 91 212 24 00\n"
        "──────────────────────\n"
        "🤝 <i>Fikringiz biz uchun muhim!</i>",
        parse_mode=ParseMode.HTML
    )
