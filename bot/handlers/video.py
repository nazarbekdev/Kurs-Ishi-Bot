from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

video_router = Router()

PRIVATE_CHANNEL_ID = -1002407784082 # bu yerga kanalning aniq ID sini yozing
VIDEO_MESSAGE_ID = 55  # kanal ichidagi video postning message_id'si


@video_router.message(Command("video"))
async def send_private_channel_video(message: Message):
    try:
        await message.bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=PRIVATE_CHANNEL_ID,
            message_id=VIDEO_MESSAGE_ID
        )
    except Exception as e:
        await message.answer("❌ Video yuborishda xatolik yuz berdi.")
        print(f"Xatolik: {e}")
