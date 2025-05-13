import asyncio
import logging
from aiogram import Bot, Dispatcher
from handlers import start, course, balance, tariffs, check, payment_user, independent_work, coupon
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    dp.include_routers(
        start.router,
        course.router,
        independent_work.independent_router,
        coupon.coupon_router,
        balance.router,
        tariffs.router,
        check.router,
        payment_user.router,
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
