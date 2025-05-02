from aiogram import Router, F
from aiogram.types import Message
import datetime

router = Router()


@router.message(F.text == "/check")
async def check_start(message: Message):
    await message.answer("To’lovni tasdiqlovchi screenshot yoki file ni yuboring.")


@router.message(F.content_type.in_({'photo', 'document'}))
async def check_payment(message: Message):
    now = datetime.datetime.now().strftime('%d.%m.%Y, %H:%M:%S')
    caption = (
        f"✨ To’lovni tasdiqlash so’rovi\n\n"
        f"User ID: {message.from_user.id}\n"
        f"Vaqt: {now}"
    )

    # Foydalanuvchiga tasdiqlash jarayoni haqida xabar yuborish
    await message.answer(
        "📝 To‘lov tasdiqlash jarayonida, 5 daqiqagacha vaqt olishi mumkin.\n"
        "Agar tasdiqlanmasa @camtest_admin yoki +998 91 212 24 00 ga murojaat qiling!"
    )

    if message.photo:
        await message.bot.send_photo(
            chat_id=-1002407784082,
            photo=message.photo[-1].file_id,
            caption=caption
        )
    elif message.document:
        await message.bot.send_document(
            chat_id=-1002407784082,
            document=message.document.file_id,
            caption=caption
        )
