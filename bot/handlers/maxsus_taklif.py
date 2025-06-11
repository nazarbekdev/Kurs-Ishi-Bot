from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums import ParseMode

maxsus_router = Router()


@maxsus_router.message(F.text == "🚀 Maxsus Kurs Ishi")
async def start_handler(message: Message):
    await message.answer(
        text=(
            "🚀 <b>Maxsus Kurs Ishi</b> xizmati haqida:\n\n"
            "Sizning ehtiyojlaringizga mos, <b>yuqori sifatli</b>, <b>plagiatsiyasiz</b> va <b>ilmiy uslubda yozilgan</b> kurs ishini birga tayyorlaymiz!\n\n"
            "📦 Xizmat tarkibi:\n"
            "1. 📚 <b>Fanga mos mavzu tanlash</b>\n"
            "2. 🧩 <b>To‘liq tuzilma</b>: Mundarija, Kirish, Asosiy boblar, Xulosa, Adabiyotlar\n"
            "3. ✍️ <b>Ilmiy uslubda matn</b> (plagiatdan xoli)\n"
            "4. 📄 <b>Metodik talablar asosida sahifalash</b>\n"
            "   - 25–50 sahifa\n"
            "   - Times New Roman 14 pt, 1.5 interval\n"
            "   - 2.5 sm margin (talablarga qarab o'zgaradi)\n"
            "5. 📚 <b>Manbalar va adabiyotlar ro‘yxati</b>\n"
            "   - So‘nggi yillardagi maqolalar, dissertatsiyalar, darsliklar\n"
            "6. 📁 <b>PDF + DOCX formatda topshirish</b>\n"
            "7. 📊 <b>Grafik, diagramma yoki jadval qo‘shish</b> (agar kerak bo‘lsa)\n"
            "8. 🔍 <b>Grammatik va uslubiy tekshiruv</b>\n"
            "9. 🖥️ <b>Qo‘shimcha xizmatlar</b> (so‘rov asosida):\n"
            "   - Prezentatsiya (PowerPoint)\n"
            "   - Himoya uchun nutq matni\n\n"
            "📞 <b>Buyurtma berish uchun admin bilan bog‘laning:</b> @camtest_admin"
        ),
        parse_mode=ParseMode.HTML
    )


@maxsus_router.message(F.text == "📕 Slayd Tayyorlash")
async def slayd_handler(message: Message):
    await message.answer(
        text=(
            "📕 <b>Slayd (Prezentatsiya) Tayyorlash</b> xizmati\n\n"
            "Biz sizning kurs ishingiz, bitiruv ishingiz yoki boshqa ilmiy ishlaringiz asosida "
            "<i>zamonaviy, estetik va informativ</i> slaydlar tayyorlab beramiz.\n\n"
            "🎯 <b>Xizmat tarkibi:</b>\n"
            "1. 📝 Kurs ishingiz asosida slayd strukturasini tuzish\n"
            "2. 🖼️ Vizual dizayn: ranglar, grafikalar, ikonlar\n"
            "3. 📊 Diagramma, grafik va jadval qo‘shish (agar mavjud bo‘lsa)\n"
            "4. 🗣️ Himoya nutqiga mos qisqa va aniq matnlar\n"
            "5. 🎨 PowerPoint (PPTX) va PDF formatlarida tayyorlab beriladi\n\n"
            "💡 <i>Maxsus talablar asosida slaydlar dizayni sozlanadi.</i>\n\n"
            "📞 <b>Buyurtma berish uchun admin bilan bog‘laning:</b> @camtest_admin"
        ),
        parse_mode=ParseMode.HTML
    )
