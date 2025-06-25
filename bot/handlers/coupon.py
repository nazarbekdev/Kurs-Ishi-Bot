# coupon.py
from aiogram import Router, F
from aiogram.types import Message
import random
import datetime
import aiohttp
import os
import pytz

coupon_router = Router()
API_URL = os.getenv('API_URL', 'http://backend:8000')
TZ = pytz.timezone('Asia/Tashkent')


async def create_coupon_api(telegram_id, coupon, expiry_time):
    async with aiohttp.ClientSession() as session:
        data = {
            "telegram_id": telegram_id,
            "coupon_type": coupon["type"],
            "value": coupon["value"],
            "text": coupon["text"],
            "expiry": expiry_time.isoformat()
        }
        async with session.post(f"{API_URL}/api/user-coupons/create/", json=data) as resp:
            if resp.status == 201:
                return await resp.json()
            else:
                try:
                    error_data = await resp.json()
                    return {"error": error_data}
                except aiohttp.ContentTypeError:
                    error_text = await resp.text()
                    return {"error": {"message": "Server xatosi yuz berdi", "details": error_text}}


def generate_coupon():
    rewards = [
        {"type": "chegirma", "value": "5%", "text": "5% chegirma"},
        {"type": "chegirma", "value": "10%", "text": "10% chegirma"},
        {"type": "chegirma", "value": "15%", "text": "15% chegirma"},
        {"type": "chegirma", "value": "20%", "text": "20% chegirma"},
        # {"type": "chegirma", "value": "25%", "text": "25% chegirma"},

        # {"type": "chegirma", "value": "30%", "text": "30% chegirma"},
        # {"type": "chegirma", "value": "35%", "text": "35% chegirma"},
        # {"type": "chegirma", "value": "40%", "text": "40% chegirma"},
        # {"type": "chegirma", "value": "45%", "text": "45% chegirma"},
        # {"type": "chegirma", "value": "50%", "text": "50% chegirma"},
        # {"type": "chegirma", "value": "30%", "text": "30% chegirma"},
    ]
    return random.choice(rewards)


@coupon_router.message(F.text == "/get_coupon")
async def get_coupon(message: Message):
    telegram_id = message.from_user.id
    # Hozirgi vaqtni Asia/Tashkent da olish
    now = datetime.datetime.now(TZ)  # To'g'ridan-to'g'ri Asia/Tashkent vaqtini olamiz

    # Foydalanuvchi mavjudligini tekshirish
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/get/{telegram_id}/") as resp:
            if resp.status != 200:
                await message.answer("Iltimos, avval /start ni bosing!")
                return

    # Yangi kupon generatsiyasi va saqlash
    coupon = generate_coupon()
    expiry_time = now + datetime.timedelta(hours=24)  # 24 soat keyin
    result = await create_coupon_api(telegram_id, coupon, expiry_time)

    if result and "error" not in result:
        await message.answer(
            f"🎉 <b>Sirli Kupon!</b>\n\n"
            f"Siz bugun yutib oldingiz:\n"
            f"💎 {coupon['text']}\n\n"
            f"⏳ Muddati: {expiry_time.strftime('%H:%M:%S %Y-%m-%d')} gacha\n"
            f"Kurs ishi va Mustaqil ish buyurtmalari berishda foydalaning va chegirmadan bahramand bo‘ling!",
            parse_mode="HTML"
        )
    else:
        error = result.get("error", {})
        if error.get("error") == "Siz bugun allaqachon kupon oldingiz!":
            existing_coupon = error.get("existing_coupon", {})
            expiry_str = existing_coupon.get("expiry", "Nomalum")
            try:
                # Backend'dan qaytgan expiry vaqtini Asia/Tashkent ga moslashtiramiz
                expiry_dt = datetime.datetime.fromisoformat(expiry_str.replace("Z", "+00:00"))
                expiry_dt = expiry_dt.astimezone(TZ)  # UTC dan Asia/Tashkent ga o'tkazamiz
                expiry_formatted = expiry_dt.strftime('%H:%M:%S %Y-%m-%d')
            except (ValueError, TypeError):
                expiry_formatted = expiry_str  # Agar formatlash ishlamasa, xom holda qoldiramiz
            await message.answer(
                f"⏳ <b>Kechirasiz!</b>\n\n"
                f"Siz bugun allaqachon kupon oldingiz:\n"
                f"💎 {existing_coupon.get('text', 'Nomalum')}\n"
                f"Muddati: {expiry_formatted} gacha\n\n"
                f"Ertaga yana urinib ko‘ring!",
                parse_mode="HTML"
            )
        else:
            await message.answer(f"Kupon yaratishda xatolik yuz berdi: {error.get('message', 'Nomalum')}")


@coupon_router.message(F.text == "🎲 Sirli Kupon")
async def get_coupon_button(message: Message):
    await get_coupon(message)
