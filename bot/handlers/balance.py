from aiogram import Router, F
from aiogram.types import Message
import aiohttp
import os

router = Router()

API_URL = os.getenv('API_URL')


@router.message(F.text == "Balans")
async def balance(message: Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/get/{message.from_user.id}/") as resp:
            if resp.status == 200:
                data = await resp.json()
                await message.answer(
                    f"Balansingiz: {data['balance']} so’m\n\nHisobingizni to’ldirish uchun:\n9860350103580741\nQobulov Nazarbek\n\nTo'lov chekini /check buyrug'i orqali yuboring!")
