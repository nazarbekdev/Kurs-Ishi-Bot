import os
import datetime
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import Message, BufferedInputFile, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from keyboards.keyboards import language_kb, confirm_kb, main_kb
import asyncio
import requests
import logging
from pathlib import Path
from utils.generate_mundarija import generate_mundarija
from utils.generate_kirish import generate_kirish
from utils.generate_I_bob import generate_bob_1
from utils.generate_I_bob import generate_bob_2
from utils.merge_docx import merge_docx_files
from utils.generate_xulosa import generate_xulosa
from utils.generate_foydalanilgan_adabiyotlar import generate_foydalanilgan_adabiyotlar
import pytz

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_logs.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

router = Router()

# Vaqt mintaqasi
TZ = pytz.timezone('Asia/Tashkent')

# Foydalanuvchi ma'lumotlarini saqlash uchun lug'at
user_data = {}

# Inline buttonlar uchun keyboardlar
language_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="O'zbekcha", callback_data="lang_uz")],
    [InlineKeyboardButton(text="Ruscha", callback_data="lang_ru")],
    [InlineKeyboardButton(text="Inglizcha", callback_data="lang_en")]
])

pages_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="10-20 sahifa", callback_data="pages_10_20")],
    [InlineKeyboardButton(text="20-30 sahifa", callback_data="pages_20_30")],
    [InlineKeyboardButton(text="30-40 sahifa", callback_data="pages_30_40")]
])

confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Ha ✅", callback_data="confirm_yes")],
    [InlineKeyboardButton(text="Yo'q ❌", callback_data="confirm_no")]
])

main_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Kurs ishi", callback_data="kurs_ishi")]
])

API_URL = os.getenv('API_URL')

# API URL'lari
GET_BALANCE_URL = f"{API_URL}/api/get/"
UPDATE_BALANCE_URL = f"{API_URL}/api/update/"


# Narx hisoblash funksiyasi
def calculate_price(page_range: str) -> int:
    if page_range == "10_20":
        return 30000
    elif page_range == "20_30":
        return 50000
    elif page_range == "30_40":
        return 70000
    return 0


# Kuponni olish funksiyasi
async def get_user_coupon(user_id: int) -> dict:
    try:
        logger.info(f"Kuponni olish: User ID: {user_id}")
        response = requests.get(f"{API_URL}/api/user-coupons/?telegram_id={user_id}", timeout=5)
        response.raise_for_status()
        coupons = response.json()

        # Faqat bugungi kunda yaratilgan, foydalanilmagan va muddati tugamagan kuponlarni tanlaymiz
        now = datetime.datetime.now(TZ)
        for coupon in coupons:
            expiry = datetime.datetime.fromisoformat(coupon['expiry'].replace("Z", "+00:00")).astimezone(TZ)
            if coupon['used'] == False and expiry > now and coupon['created_at'].startswith(now.strftime('%Y-%m-%d')):
                logger.info(f"Faol kupon topildi: User ID: {user_id}, Kupon: {coupon['text']}")
                return coupon
        logger.info(f"Faol kupon topilmadi: User ID: {user_id}")
        return None
    except requests.RequestException as e:
        logger.error(f"Kupon olishda xatolik: User ID: {user_id}, Xato: {str(e)}")
        return None


# Kuponni ishlatilgan deb belgilash funksiyasi
async def mark_coupon_as_used(coupon_id: int, user_id: int) -> bool:
    try:
        logger.info(f"Kuponni ishlatilgan deb belgilash: Coupon ID: {coupon_id}, User ID: {user_id}")
        response = requests.patch(
            f"{API_URL}/api/user-coupons/{coupon_id}/?telegram_id={user_id}",  # telegram_id qo'shildi
            json={"used": True},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        response.raise_for_status()
        logger.info(f"Kupon muvaffaqiyatli yangilandi: Coupon ID: {coupon_id}")
        return True
    except requests.RequestException as e:
        logger.error(f"Kuponni yangilashda xatolik: Coupon ID: {coupon_id}, Xato: {str(e)}")
        return False


# Chegirma hisoblash funksiyasi
def apply_coupon_discount(price: int, coupon: dict) -> tuple[int, str]:
    if not coupon or coupon['coupon_type'] != 'chegirma':
        return price, None

    discount_percentage = int(coupon['value'].replace("%", ""))
    discount_amount = (price * discount_percentage) // 100
    discounted_price = price - discount_amount
    return discounted_price, f"{discount_percentage}% chegirma qo‘llanildi"


# Balansni tekshirish funksiyasi
def check_balance(user_id: int, retries=3, delay=1) -> dict:
    for attempt in range(retries):
        try:
            logger.info(f"Balansni tekshirish: User ID: {user_id}, Urinish: {attempt + 1}/{retries}")
            response = requests.get(f"{GET_BALANCE_URL}{user_id}", timeout=5)
            response.raise_for_status()
            balance_data = response.json()
            logger.info(f"Balans olingan: User ID: {user_id}, Balans: {balance_data['balance']}")
            return balance_data
        except requests.RequestException as e:
            logger.error(f"Balans olishda xatolik: User ID: {user_id}, Xato: {str(e)}")
            if attempt < retries - 1:
                asyncio.sleep(delay)
                continue
            return None


# Balansni yangilash funksiyasi
def update_balance(user_id: int, new_balance: float, retries=5, delay=2):
    for attempt in range(retries):
        try:
            logger.info(
                f"Balansni yangilash: User ID: {user_id}, Yangi balans: {new_balance}, Urinish: {attempt + 1}/{retries}")
            response = requests.patch(
                f"{UPDATE_BALANCE_URL}{user_id}/",
                json={"balance": new_balance},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Balans muvaffaqiyatli yangilandi: User ID: {user_id}, Yangi balans: {new_balance}")
            return True
        except requests.RequestException as e:
            logger.error(f"Balans yangilashda xatolik: User ID: {user_id}, Xato: {str(e)}")
            if attempt < retries - 1:
                asyncio.sleep(delay)
                continue
            return False


# Tilga qarab xabarlar (HTML formatida)
language_messages = {
    "uz": {
        "fan": "Kurs ishi yozmoqchi bo’lgan fan yoki sohani nomini kiriting:",
        "mavzu": "Mavzu nomini kiriting:\n\nE'tibor bering!\nMavzu nomini kiritayotganda imlo qoidalariga rioya qiling!\nQisqartma so'zlardan foydalanmang!",
        "sahifa": "Kurs ishi sahifalar sonini tanlang:",
        "confirm": "📋 <b>Ma’lumotlar to’g’rimi?</b>\n\n"
                   "• <b>Til:</b> {til}\n"
                   "• <b>Fan:</b> {fan}\n"
                   "• <b>Mavzu:</b> {mavzu}\n"
                   "• <b>Sahifalar:</b> {sahifa}\n\n"
                   "💸 <b>Asl narxi:</b> <s>{price:,} so’m</s>\n"
                   "🎉 <b>Chegirma bilan:</b> {discounted_price:,} so’m <i>({discount_info})</i>\n\n"
                   "👇 Tasdiqlang yoki bekor qiling:",
        "confirm_no_coupon": "📋 <b>Ma’lumotlar to’g’rimi?</b>\n\n"
                             "• <b>Til:</b> {til}\n"
                             "• <b>Fan:</b> {fan}\n"
                             "• <b>Mavzu:</b> {mavzu}\n"
                             "• <b>Sahifalar:</b> {sahifa}\n\n"
                             "💸 <b>Narxi:</b> {price:,} so’m\n\n"
                             "👇 Tasdiqlang yoki bekor qiling:",
        "balance_error":
            "❌ <b>Balansingizda yetarli mablag' mavjud emas!</b>\nHozirgi balans: <b>{balance} so'm</b>.\n\n"
            "Iltimos, balansingizni to'ldiring.\n\n"
            "🎁 <b>Eslatma:</b> Siz chegirma kuponini olish orqali arzonlashtirilgan narxda xizmatlardan foydalanishingiz mumkin!\n"
            "➡️ <b>«🎲 Sirli Kupon»</b> tugmasini bosing yoki /get_coupon buyrug'idan foydalaning.",
        "cancel":
            "❌ <b>Amaliyot bekor qilindi.</b>\n\n"
            "🎁 <b>Eslatma:</b> Siz chegirma kuponini olish orqali ba'zi xizmatlardan chegirma bilan foydalanishingiz mumkin!\n"
            "➡️ <b>«🎲 Sirli Kupon»</b> tugmasini bosing yoki /get_coupon buyrug'idan foydalaning.",
    },
    "ru": {
        "fan": "Введите название предмета или области, по которой хотите написать курсовую работу:",
        "mavzu": "Введите название темы:\n\nОбратите внимание!\nПри вводе названия темы соблюдайте правила орфографии!\nНе используйте сокращения!",
        "sahifa": "Выберите количество страниц курсовой работы:",
        "confirm": "📋 <b>Правильны ли данные?</b>\n\n"
                   "• <b>Язык:</b> {til}\n"
                   "• <b>Предмет:</b> {fan}\n"
                   "• <b>Тема:</b> {mavzu}\n"
                   "• <b>Страницы:</b> {sahifa}\n\n"
                   "💸 <b>Изначальная стоимость:</b> <s>{price:,} сум</s>\n"
                   "🎉 <b>Со скидкой:</b> {discounted_price:,} сум <i>({discount_info})</i>\n\n"
                   "👇 Подтвердите или отмените:",
        "confirm_no_coupon": "📋 <b>Правильны ли данные?</b>\n\n"
                             "• <b>Язык:</b> {til}\n"
                             "• <b>Предмет:</b> {fan}\n"
                             "• <b>Тема:</b> {mavzu}\n"
                             "• <b>Страницы:</b> {sahifa}\n\n"
                             "💸 <b>Стоимость:</b> {price:,} сум\n\n"
                             "👇 Подтвердите или отмените:",
        "balance_error":
            "❌ <b>На вашем балансе недостаточно средств!</b>\nТекущий баланс: <b>{balance} сум</b>.\n\n"
            "Пожалуйста, пополните ваш баланс.\n\n"
            "🎁 <b>Подсказка:</b> Вы можете получить скидку, используя купон!\n"
            "➡️ Нажмите <b>«🎲 Sirli Kupon»</b> или используйте команду /get_coupon.",

        "cancel":
            "❌ <b>Операция отменена.</b>\n\n"
            "🎁 <b>Подсказка:</b> Вы можете воспользоваться скидкой, получив купон!\n"
            "➡️ Нажмите <b>«🎲 Sirli Kupon»</b> или введите /get_coupon",
    },
    "en": {
        "fan": "Enter the name of the subject or field for your coursework:",
        "mavzu": "Enter the topic name:\n\nPlease note!\nWhen entering the topic name, follow spelling rules!\nDo not use abbreviations!",
        "sahifa": "Select the number of pages for your coursework:",
        "confirm": "📋 <b>Are the details correct?</b>\n\n"
                   "• <b>Language:</b> {til}\n"
                   "• <b>Subject:</b> {fan}\n"
                   "• <b>Topic:</b> {mavzu}\n"
                   "• <b>Pages:</b> {sahifa}\n\n"
                   "💸 <b>Original Price:</b> <s>{price:,} UZS</s>\n"
                   "🎉 <b>With Discount:</b> {discounted_price:,} UZS <i>({discount_info})</i>\n\n"
                   "👇 Confirm or cancel:",
        "confirm_no_coupon": "📋 <b>Are the details correct?</b>\n\n"
                             "• <b>Language:</b> {til}\n"
                             "• <b>Subject:</b> {fan}\n"
                             "• <b>Topic:</b> {mavzu}\n"
                             "• <b>Pages:</b> {sahifa}\n\n"
                             "💸 <b>Price:</b> {price:,} UZS\n\n"
                             "👇 Confirm or cancel:",
        "balance_error":
            "❌ <b>You don't have enough balance!</b>\nCurrent balance: <b>{balance} UZS</b>.\n\n"
            "Please top up your account.\n\n"
            "🎁 <b>Tip:</b> You can use a discount coupon to reduce your payment!\n"
            "➡️ Tap <b>«🎲 Sirli Kupon»</b> or use the /get_coupon command.",

        "cancel":
            "❌ <b>Operation cancelled.</b>\n\n"
            "🎁 <b>Tip:</b> You can save money by using a discount coupon!\n"
            "➡️ Tap <b>«🎲 Sirli Kupon»</b> or type /get_coupon",
    }
}


@router.message(F.text.in_({"🎓 Kurs ishi", "/kurs_ishi"}))
async def course_start(message: Message):
    await message.answer("Kurs ishi yozish uchun dastlab namuna bilan tanishib chiqing!\n👉 @/kursishinamuna\n Bot ushbu namunalar bo'yicha tayyorlab beradi.\nSizda boshqa standart bo'lsa /admin ga murojaat qiling!!!")
    await message.answer("Qaysi tilda bo’lsin:", reply_markup=language_kb)
    user_data[message.from_user.id] = {}


@router.callback_query(F.data.startswith("lang_"))
async def get_language(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = callback.data.split("_")[1]
    til_map = {"uz": "O'zbekcha", "ru": "Ruscha", "en": "Inglizcha"}
    user_data[user_id]['til'] = til_map[lang]
    user_data[user_id]['lang_code'] = lang

    lang_messages = language_messages[lang]
    await callback.message.edit_text(lang_messages["fan"], reply_markup=None)
    await callback.answer()


@router.message(lambda message: message.from_user.id in user_data and 'fan' not in user_data[message.from_user.id])
async def get_fan(message: Message):
    user_id = message.from_user.id
    user_data[user_id]['fan'] = message.text
    lang = user_data[user_id]['lang_code']
    await message.answer(language_messages[lang]["mavzu"])


@router.message(lambda message: message.from_user.id in user_data and 'mavzu' not in user_data[message.from_user.id])
async def get_mavzu(message: Message):
    user_id = message.from_user.id
    user_data[user_id]['mavzu'] = message.text
    lang = user_data[user_id]['lang_code']
    await message.answer(language_messages[lang]["sahifa"], reply_markup=pages_kb)


@router.callback_query(F.data.startswith("pages_"))
async def get_sahifa(callback: CallbackQuery):
    user_id = callback.from_user.id
    page_range = callback.data.split("_", 1)[1]
    page_map = {"10_20": "10-20", "20_30": "20-30", "30_40": "30-40"}
    user_data[user_id]['sahifa_range'] = page_map[page_range]

    start, end = map(int, page_map[page_range].split("-"))
    user_data[user_id]['sahifa'] = (start + end) // 2

    # Narxni hisoblash
    price = calculate_price(page_range)
    user_data[user_id]['price'] = price

    # Kuponni tekshirish
    coupon = await get_user_coupon(user_id)
    user_data[user_id]['coupon'] = coupon

    # Chegirma qo‘llash
    if coupon:
        discounted_price, discount_info = apply_coupon_discount(price, coupon)
        user_data[user_id]['discounted_price'] = discounted_price
        user_data[user_id]['discount_info'] = discount_info
    else:
        user_data[user_id]['discounted_price'] = price
        user_data[user_id]['discount_info'] = None

    lang = user_data[user_id]['lang_code']
    data = user_data[user_id]
    if coupon:
        message_template = language_messages[lang]["confirm"]
        await callback.message.edit_text(
            message_template.format(
                til=data['til'],
                fan=data['fan'],
                mavzu=data['mavzu'],
                sahifa=data['sahifa_range'],
                price=price,
                discounted_price=data['discounted_price'],
                discount_info=data['discount_info']
            ),
            reply_markup=confirm_kb,
            parse_mode=ParseMode.HTML
        )
    else:
        message_template = language_messages[lang]["confirm_no_coupon"]
        await callback.message.edit_text(
            message_template.format(
                til=data['til'],
                fan=data['fan'],
                mavzu=data['mavzu'],
                sahifa=data['sahifa_range'],
                price=price
            ),
            reply_markup=confirm_kb,
            parse_mode=ParseMode.HTML
        )
    await callback.answer()


@router.callback_query(F.data == "confirm_yes")
async def confirm_course(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_data:
        await callback.message.edit_text("Ma'lumotlar topilmadi. Iltimos, jarayonni qayta boshlang.",
                                         reply_markup=main_kb, parse_mode=ParseMode.MARKDOWN)
        await callback.answer()
        return

    # Balansni tekshirish
    balance_data = check_balance(user_id)
    if not balance_data:
        await callback.message.edit_text(
            "❌ Server bilan bog‘lanishda xatolik yuz berdi. Iltimos, keyinroq urinib ko‘ring.",
            parse_mode=ParseMode.MARKDOWN)
        user_data.pop(user_id, None)
        await callback.answer()
        return

    current_balance = float(balance_data['balance'])
    price = user_data[user_id]['discounted_price']  # Chegirma qo‘llangan narxni ishlatamiz
    lang = user_data[user_id]['lang_code']

    if current_balance < price:
        await callback.message.edit_text(
            language_messages[lang]["balance_error"].format(balance=current_balance),
            parse_mode=ParseMode.HTML
        )
        user_data.pop(user_id, None)
        await callback.answer()
        return

    # Balansdan pulni kesish va yangilash
    new_balance = current_balance - price
    if not update_balance(user_id, new_balance):
        await callback.message.edit_text(
            f"❌ Balansni yangilashda xatolik yuz berdi. Hozirgi balans: {current_balance} so‘m. "
            "Iltimos, keyinroq urinib ko‘ring.",
            parse_mode=ParseMode.HTML
        )
        user_data.pop(user_id, None)
        await callback.answer()
        return

    # Kuponni ishlatilgan deb belgilash
    coupon = user_data[user_id].get('coupon')
    if coupon:
        if not await mark_coupon_as_used(coupon['id'], user_id):
            await callback.message.edit_text(
                "❌ Kuponni yangilashda xatolik yuz berdi. Iltimos, keyinroq urinib ko‘ring.",
                parse_mode=ParseMode.HTML
            )
            user_data.pop(user_id, None)
            await callback.answer()
            return

    # Kurs ishi tayyorlashni boshlash
    progress_message = await callback.message.edit_text(
        "📝 **Kurs ishi tayyorlanmoqda...**\n\n"
        f"Fan: {user_data[user_id]['fan']}\n"
        f"Mavzu: {user_data[user_id]['mavzu']}\n"
        f"Til: {user_data[user_id]['til']}\n\n"
        "⏳ [10% |██----------]\nMundarija tayyorlanmoqda...",
        parse_mode=ParseMode.MARKDOWN
    )

    # Foydalanuvchi ma'lumotlarini olish
    data = user_data[user_id]
    fan_nomi = data['fan']
    mavzu = data['mavzu']
    til = data['til']
    sahifa = data['sahifa']

    # Tilni moslashtirish
    try:
        if til == "O'zbekcha":
            til_ = "o'zbek tili"
        elif til == "Ruscha":
            til_ = "rus tili"
        else:
            til_ = "ingliz tili"

        # Mundarija generatsiya qilish
        mundarija_text, mundarija_path, chapter_1_sections, chapter_2_sections = generate_mundarija(fan_nomi, mavzu,
                                                                                                    til_)
        await asyncio.sleep(1)

        await progress_message.edit_text(
            "📝 **Kurs ishi tayyorlanmoqda...**\n\n"
            f"Fan: {fan_nomi}\n"
            f"Mavzu: {mavzu}\n"
            f"Til: {til_}\n\n"
            f"✅ **Mundarija tayyor!**\n"
            f"I bob: {chapter_1_sections['chapter_title']}\n"
            f"II bob: {chapter_2_sections['chapter_title']}\n\n"
            "⏳ [25% |███---------]\nKirish qismi tayyorlanmoqda...",
            parse_mode=ParseMode.MARKDOWN
        )

        # Kirish qismini generatsiya qilish
        kirish_path = generate_kirish(fan_nomi, mavzu, til_)
        await asyncio.sleep(1)

        await progress_message.edit_text(
            "📝 **Kurs ishi tayyorlanmoqda...**\n\n"
            f"Fan: {fan_nomi}\n"
            f"Mavzu: {mavzu}\n"
            f"Til: {til_}\n\n"
            f"✅ **Mundarija tayyor!**\n"
            f"✅ **Kirish qismi tayyor!**\n\n"
            "⏳ [40% |█████-------]\nI bob tayyorlanmoqda...",
            parse_mode=ParseMode.MARKDOWN
        )

        # I bobni generatsiya qilish
        bob_1_path = generate_bob_1(fan_nomi, mavzu, til_, chapter_1_sections, sahifa)
        await asyncio.sleep(1)

        await progress_message.edit_text(
            "📝 **Kurs ishi tayyorlanmoqda...**\n\n"
            f"Fan: {fan_nomi}\n"
            f"Mavzu: {mavzu}\n"
            f"Til: {til_}\n\n"
            f"✅ **Mundarija tayyor!**\n"
            f"✅ **Kirish qismi tayyor!**\n"
            f"✅ **I bob tayyor!**\n\n"
            "⏳ [55% |██████------]\nII bob tayyorlanmoqda...",
            parse_mode=ParseMode.MARKDOWN
        )

        # II bobni generatsiya qilish
        bob_2_path = generate_bob_2(fan_nomi, mavzu, til_, chapter_2_sections, sahifa)
        await asyncio.sleep(1)

        await progress_message.edit_text(
            "📝 **Kurs ishi tayyorlanmoqda...**\n\n"
            f"Fan: {fan_nomi}\n"
            f"Mavzu: {mavzu}\n"
            f"Til: {til_}\n\n"
            f"✅ **Mundarija tayyor!**\n"
            f"✅ **Kirish qismi tayyor!**\n"
            f"✅ **I bob tayyor!**\n"
            f"✅ **II bob tayyor!**\n\n"
            "⏳ [70% |████████----]\nXulosa tayyorlanmoqda...",
            parse_mode=ParseMode.MARKDOWN
        )

        # Xulosa qismini generatsiya qilish
        xulosa_path = generate_xulosa(fan_nomi, mavzu, til_, sahifa, chapter_1_sections, chapter_2_sections)
        await asyncio.sleep(1)

        await progress_message.edit_text(
            "📝 **Kurs ishi tayyorlanmoqda...**\n\n"
            f"Fan: {fan_nomi}\n"
            f"Mavzu: {mavzu}\n"
            f"Til: {til_}\n\n"
            f"✅ **Mundarija tayyor!**\n"
            f"✅ **Kirish qismi tayyor!**\n"
            f"✅ **I bob tayyor!**\n"
            f"✅ **II bob tayyor!**\n"
            f"✅ **Xulosa tayyor!**\n\n"
            "⏳ [85% |██████████--]\nAdabiyotlar tayyorlanmoqda...",
            parse_mode=ParseMode.MARKDOWN
        )

        # Foydalanilgan adabiyotlar qismini generatsiya qilish
        adabiyotlar_path = generate_foydalanilgan_adabiyotlar(fan_nomi, mavzu, sahifa, til_, chapter_1_sections,
                                                              chapter_2_sections)
        await asyncio.sleep(1)

        await progress_message.edit_text(
            "📝 **Kurs ishi tayyorlanmoqda...**\n\n"
            f"Fan: {fan_nomi}\n"
            f"Mavzu: {mavzu}\n"
            f"Til: {til_}\n\n"
            f"✅ **Mundarija tayyor!**\n"
            f"✅ **Kirish qismi tayyor!**\n"
            f"✅ **I bob tayyor!**\n"
            f"✅ **II bob tayyor!**\n"
            f"✅ **Xulosa tayyor!**\n"
            f"✅ **Adabiyotlar tayyor!**\n\n"
            "⏳ [95% |███████████-]\nFayllar birlashtirilmoqda...",
            parse_mode=ParseMode.MARKDOWN
        )

        # Docx fayllarni birlashtirish
        merged_path = f"generated_docs/merged_{mavzu}_{til_.lower().replace(' ', '_')}.docx"
        merge_docx_files([mundarija_path, kirish_path, bob_1_path, bob_2_path, xulosa_path, adabiyotlar_path],
                         merged_path)
        await asyncio.sleep(1)

    except Exception as e:
        await progress_message.edit_text(
            f"❌ **Xatolik yuz berdi:** {str(e)}\nIltimos, qaytadan urinib ko‘ring.",
            parse_mode=ParseMode.MARKDOWN
        )
        user_data.pop(user_id, None)
        await callback.answer()
        return

    # Birlashtirilgan docx faylni yuborish
    if not Path(merged_path).exists():
        await callback.message.answer("❌ Xatolik: Birlashtirilgan fayl topilmadi!", parse_mode=ParseMode.MARKDOWN)
        user_data.pop(user_id, None)
        await callback.answer()
        return

    with open(merged_path, 'rb') as file:
        file_content = file.read()
    document = BufferedInputFile(file_content, filename=f"{mavzu}.docx")

    await callback.message.answer_document(document)
    await callback.message.answer(
        f"✅ **Xizmatimizdan foydalanganingiz uchun tashakkur!**\n",
        reply_markup=main_kb,
        parse_mode=ParseMode.MARKDOWN
    )

    await progress_message.edit_text(
        "🎉 **Kurs ishi tayyor!**\n\n"
        f"Fan: {fan_nomi}\n"
        f"Mavzu: {mavzu}\n"
        f"Til: {til_}\n\n"
        "✅ [100% |████████████]\nFayl yuklab olindi!",
        parse_mode=ParseMode.MARKDOWN
    )

    # Fayllarni o‘chirish
    paths_to_delete = [
        mundarija_path,
        kirish_path,
        bob_1_path,
        bob_2_path,
        xulosa_path,
        adabiyotlar_path,
        merged_path
    ]

    for path in paths_to_delete:
        try:
            if os.path.exists(path):
                os.remove(path)
                print(f"Fayl o‘chirildi: {path}")
        except Exception as e:
            print(f"Fayl o‘chirishda xatolik: {path}, Xato: {str(e)}")

    # Foydalanuvchi ma'lumotlarini o‘chirish
    user_data.pop(user_id, None)
    await callback.answer()


@router.callback_query(F.data == "confirm_no")
async def cancel_course(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = user_data[user_id]['lang_code']
    await callback.message.edit_text(language_messages[lang]["cancel"], reply_markup=main_kb,
                                     parse_mode=ParseMode.HTML)
    user_data.pop(user_id, None)
    await callback.answer()
