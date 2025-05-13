from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import os
import aiohttp

router = Router()

ADMIN_ID = 5605407368
API_URL = os.getenv('API_URL')


# States
class PaymentStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_amount = State()


# Joriy balansni olish funksiyasi
async def get_current_balance(user_id: int) -> float:
    async with aiohttp.ClientSession() as session:
        url = f"{API_URL}/api/get/{user_id}/"
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                return float(data.get('balance', 0.0))
            else:
                raise Exception(f"Balansni olishda xatolik: Status {resp.status}, {await resp.text()}")


# /payment_user komandasi
@router.message(Command('payment_user'))
async def payment_user_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Sizda bu komanda uchun ruxsat yo'q.")
        return
    await message.answer("1. Foydalanuvchi telegram ID sini kiriting:")
    await state.set_state(PaymentStates.waiting_for_user_id)


# User ID qabul qilish
@router.message(PaymentStates.waiting_for_user_id)
async def get_user_id(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
        await state.update_data(user_id=user_id)
        await message.answer("2. To’lov miqdorini kiriting:")
        await state.set_state(PaymentStates.waiting_for_amount)
    except ValueError:
        await message.answer("❗ Noto'g'ri ID. Iltimos, raqam kiriting.")


# Amount qabul qilish va balansni yangilash
@router.message(PaymentStates.waiting_for_amount)
async def get_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
        if amount <= 0:
            await message.answer("❗ To'lov miqdori 0 dan katta bo'lishi kerak!")
            return

        data = await state.get_data()
        user_id = data.get('user_id')

        # Joriy balansni olish
        current_balance = await get_current_balance(user_id)
        new_balance = current_balance + amount  # Mavjud balansga yangi miqdorni qo‘shish

        # Balansni yangilash
        async with aiohttp.ClientSession() as session:
            url = f"{API_URL}/api/update/{user_id}/"
            payload = {"balance": new_balance}
            headers = {
                "Content-Type": "application/json",
            }
            async with session.patch(url, json=payload, headers=headers) as resp:
                if resp.status in (200, 202):
                    await message.answer(f"✅ Balans muvaffaqiyatli to’ldirildi.\n"
                                         f"Eski balans: {current_balance} so‘m\n"
                                         f"Yangi balans: {new_balance} so‘m")
                    await message.bot.send_message(
                        chat_id=user_id,
                        text=f"✅ Balansingiz to’ldirildi!\n"
                             f"Balans: {new_balance} so‘m\n"
                             f"Endi kurs ishini tayyorlashingiz mumkin!"
                    )
                else:
                    error_text = await resp.text()
                    await message.answer(f"❌ Xatolik yuz berdi. Status: {resp.status}\n{error_text}")

    except ValueError:
        await message.answer("❗ Noto'g'ri to'lov miqdori. Raqam kiriting.")
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")
    finally:
        await state.clear()
