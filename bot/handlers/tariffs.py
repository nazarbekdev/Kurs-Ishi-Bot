from aiogram import Router, F
from aiogram.types import Message

router = Router()


@router.message(F.text == "Tariflar")
async def tariffs(message: Message):
    await message.answer(
        "Tariflar:\n\n• 10-20 sahifa: 30,000 so'm\n• 20-30 sahifa: 50,000 so'm\n• 30-40 sahifa: 70,000 so'm\n\n"
        "Qo'shimcha xizmatlar uchun: @camtest_admin")
