from aiogram import Router, F
from aiogram.types import Message
import datetime

router = Router()


@router.message(F.text == "/check")
async def check_start(message: Message):
    await message.answer(
        "📸 <b>To‘lovni Tasdiqlash</b>\n\n"
        "Iltimos, to‘lovni tasdiqlovchi <i>screenshot</i> yoki <i>fayl</i> ni yuboring.\n\n"
        "⚠️ Yuborishdan oldin to‘lov ma'lumotlari aniq ko‘rinishiga ishonch hosil qiling!",
        parse_mode="HTML"
    )


@router.message(F.content_type.in_({'photo', 'document'}))
async def check_payment(message: Message):
    now = datetime.datetime.now().strftime('%d.%m.%Y, %H:%M:%S')
    caption = (
        "✨ <b>To‘lovni Tasdiqlash So‘rovi</b>\n\n"
        f"👤 <b>User ID:</b> <code>{message.from_user.id}</code>\n"
        f"⏰ <b>Vaqt:</b> {now}\n"
        f"📎 <b>Fayl turi:</b> {'Rasm' if message.photo else 'Dokument'}"
    )

    # Foydalanuvchiga tasdiqlash jarayoni haqida xabar yuborish
    await message.answer(
        "⏳ <b>Tasdiqlash Jarayoni</b>\n\n"
        "To‘lov tasdiqlash jarayonida, bu 5 daqiqagacha vaqt olishi mumkin.\n\n"
        "📞 <b>Agar tasdiqlanmasa, murojaat qiling:</b>\n"
        "- 👉 @camtest_admin\n"
        "- 📱 +998 91 212 24 00",
        parse_mode="HTML"
    )

    # Admin guruhiga yuborish
    if message.photo:
        await message.bot.send_photo(
            chat_id=-1002407784082,
            photo=message.photo[-1].file_id,
            caption=caption,
            parse_mode="HTML"
        )
    elif message.document:
        await message.bot.send_document(
            chat_id=-1002407784082,
            document=message.document.file_id,
            caption=caption,
            parse_mode="HTML"
        )
