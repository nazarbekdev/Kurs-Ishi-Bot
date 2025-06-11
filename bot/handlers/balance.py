from aiogram import Router, F
from aiogram.types import Message
import aiohttp
import os

router = Router()

API_URL = os.getenv('API_URL')


@router.message(F.text.in_({"💰 Balans", "/balans"}))
async def balance(message: Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/get/{message.from_user.id}/") as resp:
            if resp.status == 200:
                data = await resp.json()
                await message.answer(
                    f"📊 **Balans Ma'lumotlari**\n\n"
                    f"💰 *Joriy balansingiz:* {data['balance']} so’m\n\n"
                    f"💸 ***Hisobni to'ldirish uchun:***\n"
                    f"`9860350103580741`\n"
                    f"Qobulov Nazarbek\n\n"
                    f"✅ To'lov chekini yuborish uchun: /check buyrug'ini ishlatib, chekni rasm sifatida yuboring!",
                    parse_mode="Markdown"
                )
            else:
                await message.answer(
                    "❌ Kechirasiz, balansni olishda xatolik yuz berdi. Iltimos, keyinroq urinib ko‘ring!",
                    parse_mode="Markdown"
                )
