from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv
import aiohttp
import os

load_dotenv()

msg_router = Router()
API_URL = os.getenv('API_URL')

ADMIN_TELEGRAM_ID = 5605407368  # Bu yerga admin telegram ID sini yozing
# ADMIN_TELEGRAM_ID = os.getenv('ADMIN_TELEGRAM_ID')  # Bu yerga admin telegram ID sini yozing
PRIVATE_CHANNEL_ID = -1002407784082  # Kanal ID sini yozing

# Boshlang'ich holatda admindan xabar ID so'rash uchun dictionary
admin_waiting_for_msg_id = set()


@msg_router.message(Command("message"))
async def message_command(message: Message):
    print('admin:', ADMIN_TELEGRAM_ID)
    if message.from_user.id != ADMIN_TELEGRAM_ID:
        await message.answer("❌ Sizda bu buyruqni ishlatish huquqi yo'q.")
        return

    await message.answer("Iltimos, kanaldagi postning xabar ID sini kiriting:")
    admin_waiting_for_msg_id.add(message.from_user.id)


@msg_router.message()
async def handle_message_id(message: Message):
    if message.from_user.id not in admin_waiting_for_msg_id:
        return  # Faqat admindan keyingi xabarlarni qabul qilamiz

    try:
        msg_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Iltimos, faqat raqam ko'rinishida xabar ID ni kiriting.")
        return

    admin_waiting_for_msg_id.remove(message.from_user.id)

    await message.answer("Xabar barcha foydalanuvchilarga yuborilmoqda...")

    # Foydalanuvchilar ro'yxatini olish
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/users/") as resp:
            if resp.status != 200:
                await message.answer("❌ Foydalanuvchilar ro'yxatini olishda xatolik yuz berdi.")
                return
            users = await resp.json()

    count = 0
    errors = 0

    for user in users:
        chat_id = user.get('telegram_id')
        if not chat_id:
            continue
        try:
            await message.bot.copy_message(
                chat_id=chat_id,
                from_chat_id=PRIVATE_CHANNEL_ID,
                message_id=msg_id
            )
            count += 1
        except Exception as e:
            print(f"Xatolik {chat_id} ga yuborishda: {e}")
            errors += 1

    await message.answer(f"✅ Xabar {count} foydalanuvchiga yuborildi.\n❌ {errors} ta xatolik yuz berdi.")
