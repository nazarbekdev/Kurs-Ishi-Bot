from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums import ParseMode

admin_router = Router()


@admin_router.message(F.text == "👨‍💼Admins")
async def start_handler(message: Message):
    await message.answer(
        "📞 <b>Admin bilan aloqa</b>\n"
        "──────────────────────\n"
        "📬 <b>Taklif yoki savollar</b> bo‘yicha:\n"
        "🔗 <a href='https://t.me/camtest_admin'>@camtest_admin</a>\n\n"
        "👨‍💻 <b>Bot dasturchisi:</b>\n"
        "🔗 <a href='https://t.me/mr_uzdev'>@mr_uzdev</a>\n"
        "──────────────────────\n"
        "🤝 <i>Fikringiz biz uchun muhim!</i>",
        parse_mode=ParseMode.HTML
    )
