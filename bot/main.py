import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from dotenv import load_dotenv
from handlers import (
    start, course, balance, tariffs, check, payment_user,
    independent_work, coupon, admin, video, guide, send_message_for_users, maxsus_taklif
)

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Botni ishga tushurish"),
        BotCommand(command="kurs_ishi", description="Kurs Ishi tayyorlash"),
        BotCommand(command="mustaqil_ish", description="Mustaqil Ish tayyorlash"),
        BotCommand(command="tariflar", description="Tariflar ro‘yxati"),
        BotCommand(command="video", description="Kanal videoni ko‘rish"),
        BotCommand(command="get_coupon", description="Chegirma kupon olish"),
        BotCommand(command="balans", description="Balansni ko‘rish"),
        BotCommand(command="check", description="Balansni to'ldirish"),
    ]
    await bot.set_my_commands(commands)


async def main():
    dp.include_routers(
        start.router,
        course.router,
        maxsus_taklif.maxsus_router,
        admin.admin_router,
        independent_work.independent_router,
        coupon.coupon_router,
        balance.router,
        tariffs.router,
        check.router,
        payment_user.router,
        video.video_router,
        guide.qollanma_router,
        send_message_for_users.msg_router,
    )

    # Komandalarni sozlash
    await set_bot_commands(bot)

    # Botni ishga tushirish
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
