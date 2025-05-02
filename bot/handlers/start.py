from aiogram import Router, F
from aiogram.types import Message
from keyboards.keyboards import main_kb
import aiohttp
import os

router = Router()

API_URL = os.getenv('API_URL')


@router.message(F.text == "/start")
async def start_handler(message: Message):
    await save_user(message)
    await message.answer("Assalomu alaykum, Kurs Ishi Robot ga xush kelibsiz!\n\nQuyidagi xizmatlardan birini tanlang:", reply_markup=main_kb)


async def save_user(message: Message):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}/api/create/", json={
            "full_name": message.from_user.full_name,
            "telegram_id": message.from_user.id
        }) as resp:
            if resp.status == 201:
                print('User saved')
