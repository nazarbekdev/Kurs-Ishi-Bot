import os
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import Message, BufferedInputFile, CallbackQuery
import asyncio
import requests
import logging
from pathlib import Path
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.keyboards import main_kb

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_logs.log"),  # Loglarni faylga yozish
        logging.StreamHandler()  # Konsolga chiqarish
    ]
)

logger = logging.getLogger(__name__)

# Mustaqil ish uchun generatsiya funksiyalari
from mustaqil_ish_utils.mundarija import generate_mundarija
from mustaqil_ish_utils.kirish import generate_kirish
from mustaqil_ish_utils.asosiy import generate_asosiy
from mustaqil_ish_utils.xulosa import generate_xulosa
from mustaqil_ish_utils.adabiyotlar import generate_foydalanilgan_adabiyotlar
from mustaqil_ish_utils.utils import merge_docs

# Alohida router yaratish
independent_router = Router()

# Inline buttonlar uchun keyboardlar
language_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="O'zbekcha", callback_data="indep_lang_uz")],
    [InlineKeyboardButton(text="Ruscha", callback_data="indep_lang_ru")],
    [InlineKeyboardButton(text="Inglizcha", callback_data="indep_lang_en")]
])

confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Ha ✅", callback_data="indep_confirm_yes")],
    [InlineKeyboardButton(text="Yo'q ❌", callback_data="indep_confirm_no")]
])

# Foydalanuvchi ma'lumotlarini saqlash uchun lug'at
independent_user_data = {}

# API sozlamalari va balans funksiyalari (oldin yozilganlarni qayta ishlatamiz)
API_URL = os.getenv('API_URL')
GET_BALANCE_URL = f"{API_URL}/api/get/"
UPDATE_BALANCE_URL = f"{API_URL}/api/update/"

PRICE = 7000


# Kuponni olish funksiyasi
async def get_user_coupon(user_id: int) -> dict:
    try:
        logger.info(f"Kuponni olish: User ID: {user_id}")
        response = requests.get(f"{API_URL}/api/user-coupons/?telegram_id={user_id}", timeout=5)
        response.raise_for_status()
        coupons = response.json()

        # Faqat bugungi kunda yaratilgan, foydalanilmagan va muddati tugamagan kuponlarni tanlaymiz
        from datetime import datetime
        import pytz
        TZ = pytz.timezone('Asia/Tashkent')
        now = datetime.now(TZ)
        for coupon in coupons:
            expiry = datetime.fromisoformat(coupon['expiry'].replace("Z", "+00:00")).astimezone(TZ)
            if not coupon['used'] and expiry > now and coupon['created_at'].startswith(now.strftime('%Y-%m-%d')):
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
            f"{API_URL}/api/user-coupons/{coupon_id}/?telegram_id={user_id}",
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


def check_balance(user_id: int, retries=3, delay=1) -> dict:
    for attempt in range(retries):
        try:
            logger.info(f"Balansni tekshirish: User ID: {user_id}, Urinish: {attempt + 1}/{retries}")
            response = requests.get(f"{GET_BALANCE_URL}{user_id}", timeout=5)
            response.raise_for_status()
            balance_data = response.json()
            return balance_data
        except requests.Timeout:
            if attempt < retries - 1:
                asyncio.sleep(delay)
                continue
            return None
        except (requests.HTTPError, requests.RequestException):
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


# Tilga qarab xabarlar
language_messages = {
    "uz": {
        "fan": "Mustaqil ish yozmoqchi bo’lgan fan yoki sohani nomini kiriting:",
        "mavzu": "Mavzu nomini kiriting:\n\nE'tibor bering!\nMavzu nomini kiritayotganda imlo qoidalariga rioya qiling!\nQisqartma so'zlardan foydalanmang!",
        "confirm": "📋 <b>Ma’lumotlar to’g’rimi?</b>\n\n"
                   "• <b>Til:</b> {til}\n"
                   "• <b>Fan:</b> {fan}\n"
                   "• <b>Mavzu:</b> {mavzu}\n\n"
                   "💸 <b>Asl narxi:</b> <s>{price:,} so’m</s>\n"
                   "🎉 <b>Chegirma bilan:</b> {discounted_price:,} so’m <i>({discount_info})</i>\n\n"
                   "👇 Tasdiqlang yoki bekor qiling:",
        "confirm_no_coupon": "📋 <b>Ma’lumotlar to’g’rimi?</b>\n\n"
                             "• <b>Til:</b> {til}\n"
                             "• <b>Fan:</b> {fan}\n"
                             "• <b>Mavzu:</b> {mavzu}\n\n"
                             "💸 <b>Narxi:</b> {price:,} so’m\n\n"
                             "👇 Tasdiqlang yoki bekor qiling:",
        "balance_error": "❌ Balansingizda yetarli mablag' mavjud emas! Hozirgi balans: {balance} so'm.\nIltimos, balansingizni to'ldiring.",
        "cancel": "Bekor qilindi."
    },
    "ru": {
        "fan": "Введите название предмета или области, по которой хотите написать самостоятельную работу:",
        "mavzu": "Введите название темы:\n\nОбратите внимание!\nПри вводе названия темы соблюдайте правила орфографии!\nНе используйте сокращения!",
        "confirm": "📋 <b>Правильны ли данные?</b>\n\n"
                   "• <b>Язык:</b> {til}\n"
                   "• <b>Предмет:</b> {fan}\n"
                   "• <b>Тема:</b> {mavzu}\n\n"
                   "💸 <b>Изначальная стоимость:</b> <s>{price:,} сум</s>\n"
                   "🎉 <b>Со скидкой:</b> {discounted_price:,} сум <i>({discount_info})</i>\n\n"
                   "👇 Подтвердите или отмените:",
        "confirm_no_coupon": "📋 <b>Правильны ли данные?</b>\n\n"
                             "• <b>Язык:</b> {til}\n"
                             "• <b>Предмет:</b> {fan}\n"
                             "• <b>Тема:</b> {mavzu}\n\n"
                             "💸 <b>Стоимость:</b> {price:,} сум\n\n"
                             "👇 Подтвердите или отмените:",
        "balance_error": "❌ На вашем балансе недостаточно средств! Текущий баланс: {balance} сум.\nПожалуйста, пополните баланс.",
        "cancel": "Отменено."
    },
    "en": {
        "fan": "Enter the name of the subject or field for your independent study:",
        "mavzu": "Enter the topic name:\n\nPlease note!\nWhen entering the topic name, follow spelling rules!\nDo not use abbreviations!",
        "confirm": "📋 <b>Are the details correct?</b>\n\n"
                   "• <b>Language:</b> {til}\n"
                   "• <b>Subject:</b> {fan}\n"
                   "• <b>Topic:</b> {mavzu}\n\n"
                   "💸 <b>Original Price:</b> <s>{price:,} UZS</s>\n"
                   "🎉 <b>With Discount:</b> {discounted_price:,} UZS <i>({discount_info})</i>\n\n"
                   "👇 Confirm or cancel:",
        "confirm_no_coupon": "📋 <b>Are the details correct?</b>\n\n"
                             "• <b>Language:</b> {til}\n"
                             "• <b>Subject:</b> {fan}\n"
                             "• <b>Topic:</b> {mavzu}\n\n"
                             "💸 <b>Price:</b> {price:,} UZS\n\n"
                             "👇 Confirm or cancel:",
        "balance_error": "❌ Insufficient funds in your balance! Current balance: {balance} UZS.\nPlease top up your balance.",
        "cancel": "Cancelled."
    }
}


@independent_router.message(F.text == "📄 Mustaqil ish")
async def independent_start(message: Message):
    await message.answer("Qaysi tilda bo’lsin:", reply_markup=language_kb)
    independent_user_data[message.from_user.id] = {}


@independent_router.callback_query(F.data.startswith("indep_lang_"))
async def get_language(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = callback.data.split("_")[2]
    til_map = {"uz": "O'zbekcha", "ru": "Ruscha", "en": "Inglizcha"}
    independent_user_data[user_id] = {'til': til_map[lang], 'lang_code': lang}

    lang_messages = language_messages[lang]
    await callback.message.edit_text(lang_messages["fan"], reply_markup=None)
    await callback.answer()


@independent_router.message(
    lambda message: message.from_user.id in independent_user_data and 'fan' not in independent_user_data[
        message.from_user.id])
async def get_fan(message: Message):
    user_id = message.from_user.id
    independent_user_data[user_id]['fan'] = message.text
    lang = independent_user_data[user_id]['lang_code']
    await message.answer(language_messages[lang]["mavzu"])


@independent_router.message(
    lambda message: message.from_user.id in independent_user_data and 'mavzu' not in independent_user_data[
        message.from_user.id])
async def get_mavzu(message: Message):
    user_id = message.from_user.id
    independent_user_data[user_id]['mavzu'] = message.text
    lang = independent_user_data[user_id]['lang_code']
    data = independent_user_data[user_id]

    # Narxni belgilash
    data['price'] = PRICE

    # Kuponni tekshirish
    coupon = await get_user_coupon(user_id)
    data['coupon'] = coupon

    # Chegirma qo‘llash
    if coupon:
        discounted_price, discount_info = apply_coupon_discount(data['price'], coupon)
        data['discounted_price'] = discounted_price
        data['discount_info'] = discount_info
    else:
        data['discounted_price'] = data['price']
        data['discount_info'] = None

    # Xabarni shakllantirish
    if coupon:
        message_template = language_messages[lang]["confirm"]
        await message.answer(
            message_template.format(
                til=data['til'],
                fan=data['fan'],
                mavzu=data['mavzu'],
                price=data['price'],
                discounted_price=data['discounted_price'],
                discount_info=data['discount_info']
            ),
            reply_markup=confirm_kb,
            parse_mode=ParseMode.HTML  # HTML parse_mode ishlatildi
        )
    else:
        message_template = language_messages[lang]["confirm_no_coupon"]
        await message.answer(
            message_template.format(
                til=data['til'],
                fan=data['fan'],
                mavzu=data['mavzu'],
                price=data['price']
            ),
            reply_markup=confirm_kb,
            parse_mode=ParseMode.HTML  # HTML parse_mode ishlatildi
        )


@independent_router.callback_query(F.data == "indep_confirm_yes")
async def confirm_independent(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in independent_user_data or not independent_user_data[user_id]:
        await callback.message.edit_text(
            "Ma'lumotlar topilmadi. Iltimos, jarayonni qayta boshlang.",
            reply_markup=main_kb,
            parse_mode=ParseMode.HTML  # HTML ga o'zgartirildi
        )
        await callback.answer()
        return

    balance_data = check_balance(user_id)
    if not balance_data:
        await callback.message.edit_text(
            "❌ Server bilan bog‘lanishda xatolik yuz berdi. Iltimos, keyinroq urinib ko‘ring.",
            parse_mode=ParseMode.HTML  # HTML ga o'zgartirildi
        )
        independent_user_data.pop(user_id, None)
        await callback.answer()
        return

    current_balance = float(balance_data['balance'])
    price = independent_user_data[user_id]['discounted_price']  # Chegirmali narxni ishlatamiz
    lang = independent_user_data[user_id]['lang_code']

    if current_balance < price:
        await callback.message.edit_text(
            language_messages[lang]["balance_error"].format(balance=current_balance),
            parse_mode=ParseMode.HTML  # HTML ga o'zgartirildi
        )
        independent_user_data.pop(user_id, None)
        await callback.answer()
        return

    new_balance = current_balance - price
    if not update_balance(user_id, new_balance):
        await callback.message.edit_text(
            f"❌ Balansni yangilashda xatolik yuz berdi. Hozirgi balans: {current_balance} so‘m. "
            "Iltimos, keyinroq urinib ko‘ring.",
            parse_mode=ParseMode.HTML  # HTML ga o'zgartirildi
        )
        independent_user_data.pop(user_id, None)
        await callback.answer()
        return

    # Kuponni ishlatilgan deb belgilash
    coupon = independent_user_data[user_id].get('coupon')
    if coupon:
        if not await mark_coupon_as_used(coupon['id'], user_id):
            await callback.message.edit_text(
                "❌ Kuponni yangilashda xatolik yuz berdi. Iltimos, keyinroq urinib ko‘ring.",
                parse_mode=ParseMode.HTML  # HTML ga o'zgartirildi
            )
            independent_user_data.pop(user_id, None)
            await callback.answer()
            return

    data = independent_user_data[user_id]
    fan_nomi = data['fan']
    mavzu = data['mavzu']
    til = data['til']

    if til == "O'zbekcha":
        til_ = "o'zbek tili"
    elif til == "Ruscha":
        til_ = "rus tili"
    else:
        til_ = "ingliz tili"

    progress_message = await callback.message.edit_text(
        "📝 <b>Mustaqil ish tayyorlanmoqda...</b>\n\n"
        f"Fan: {fan_nomi}\n"
        f"Mavzu: {mavzu}\n"
        f"Til: {til}\n\n"
        "⏳ [10% |██----------]\nMundarija tayyorlanmoqda...",
        parse_mode=ParseMode.HTML  # HTML ga o'zgartirildi
    )

    try:
        mundarija_path, reja_items = generate_mundarija(fan_nomi, mavzu, til_)
        await asyncio.sleep(1)

        await progress_message.edit_text(
            "📝 <b>Mustaqil ish tayyorlanmoqda...</b>\n\n"
            f"Fan: {fan_nomi}\n"
            f"Mavzu: {mavzu}\n"
            f"Til: {til}\n\n"
            f"✅ <b>Mundarija tayyor!</b>\n\n"
            "⏳ [25% |███---------]\nKirish qismi tayyorlanmoqda...",
            parse_mode=ParseMode.HTML
        )

        kirish_path = generate_kirish(fan_nomi, mavzu, til_)
        await asyncio.sleep(1)

        await progress_message.edit_text(
            "📝 <b>Mustaqil ish tayyorlanmoqda...</b>\n\n"
            f"Fan: {fan_nomi}\n"
            f"Mavzu: {mavzu}\n"
            f"Til: {til}\n\n"
            f"✅ <b>Mundarija tayyor!</b>\n"
            f"✅ <b>Kirish qismi tayyor!</b>\n\n"
            "⏳ [50% |██████------]\nAsosiy qism tayyorlanmoqda...",
            parse_mode=ParseMode.HTML
        )

        asosiy_path = generate_asosiy(fan_nomi, mavzu, til_, reja_items, 13)
        await asyncio.sleep(1)

        await progress_message.edit_text(
            "📝 <b>Mustaqil ish tayyorlanmoqda...</b>\n\n"
            f"Fan: {fan_nomi}\n"
            f"Mavzu: {mavzu}\n"
            f"Til: {til}\n\n"
            f"✅ <b>Mundarija tayyor!</b>\n"
            f"✅ <b>Kirish qismi tayyor!</b>\n"
            f"✅ <b>Asosiy qism tayyor!</b>\n\n"
            "⏳ [75% |█████████---]\nXulosa tayyorlanmoqda...",
            parse_mode=ParseMode.HTML
        )

        xulosa_path = generate_xulosa(fan_nomi, mavzu, til_)
        await asyncio.sleep(1)

        await progress_message.edit_text(
            "📝 <b>Mustaqil ish tayyorlanmoqda...</b>\n\n"
            f"Fan: {fan_nomi}\n"
            f"Mavzu: {mavzu}\n"
            f"Til: {til}\n\n"
            f"✅ <b>Mundarija tayyor!</b>\n"
            f"✅ <b>Kirish qismi tayyor!</b>\n"
            f"✅ <b>Asosiy qism tayyor!</b>\n"
            f"✅ <b>Xulosa tayyor!</b>\n\n"
            "⏳ [90% |███████████-]\nAdabiyotlar tayyorlanmoqda...",
            parse_mode=ParseMode.HTML
        )

        adabiyotlar_path = generate_foydalanilgan_adabiyotlar(fan_nomi, mavzu, til_, 13, reja_items)
        await asyncio.sleep(1)

        await progress_message.edit_text(
            "📝 <b>Mustaqil ish tayyorlanmoqda...</b>\n\n"
            f"Fan: {fan_nomi}\n"
            f"Mavzu: {mavzu}\n"
            f"Til: {til}\n\n"
            f"✅ <b>Mundarija tayyor!</b>\n"
            f"✅ <b>Kirish qismi tayyor!</b>\n"
            f"✅ <b>Asosiy qism tayyor!</b>\n"
            f"✅ <b>Xulosa tayyor!</b>\n"
            f"✅ <b>Adabiyotlar tayyor!</b>\n\n"
            "⏳ [95% |███████████-]\nFayllar birlashtirilmoqda...",
            parse_mode=ParseMode.HTML
        )

        merged_path = f"generated_docs/merged_{mavzu}_{til_.lower().replace(' ', '_')}.docx"
        merge_docs(merged_path, [mundarija_path, kirish_path, asosiy_path, xulosa_path, adabiyotlar_path])
        await asyncio.sleep(1)

    except Exception as e:
        await progress_message.edit_text(
            f"❌ <b>Xatolik yuz berdi:</b> {str(e)}\nIltimos, qaytadan urinib ko‘ring.",
            parse_mode=ParseMode.HTML
        )
        independent_user_data.pop(user_id, None)
        await callback.answer()
        return

    if not Path(merged_path).exists():
        await callback.message.answer("❌ Xatolik: Birlashtirilgan fayl topilmadi!", parse_mode=ParseMode.HTML)
        independent_user_data.pop(user_id, None)
        await callback.answer()
        return

    with open(merged_path, 'rb') as file:
        file_content = file.read()
    document = BufferedInputFile(file_content, filename=f"{mavzu}.docx")

    await callback.message.answer_document(document)
    await callback.message.answer(
        f"✅ <b>Xizmatimizdan foydalanganingiz uchun tashakkur!</b>\n",
        reply_markup=main_kb,
        parse_mode=ParseMode.HTML
    )

    await progress_message.edit_text(
        "🎉 <b>Mustaqil ish tayyor!</b>\n\n"
        f"Fan: {fan_nomi}\n"
        f"Mavzu: {mavzu}\n"
        f"Til: {til}\n\n"
        "✅ [100% |████████████]\nFayl yuklab olindi!",
        parse_mode=ParseMode.HTML
    )

    paths_to_delete = [mundarija_path, kirish_path, asosiy_path, xulosa_path, adabiyotlar_path, merged_path]
    for path in paths_to_delete:
        try:
            if os.path.exists(path):
                os.remove(path)
                print(f"Fayl o‘chirildi: {path}")
        except Exception as e:
            print(f"Fayl o‘chirishda xatolik: {path}, Xato: {str(e)}")

    independent_user_data.pop(user_id, None)
    await callback.answer()


@independent_router.callback_query(F.data == "indep_confirm_no")
async def cancel_independent(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = independent_user_data[user_id]['lang_code']
    lnm = language_messages[lang]["cancel"]
    await callback.message.answer(lnm, reply_markup=main_kb, parse_mode=ParseMode.MARKDOWN)
    independent_user_data.pop(user_id, None)
    await callback.answer()
