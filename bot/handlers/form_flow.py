from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import requests
import os
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL")

router = Router()


class CourseWorkForm(StatesGroup):
    field = State()
    topic = State()
    university = State()
    pages = State()
    language = State()


@router.callback_query()
async def process_field(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(field=callback.data)
    await callback.message.answer("Kurs ishi mavzusini kiriting:")
    await state.set_state(CourseWorkForm.topic)
    await callback.message.delete()


@router.message(CourseWorkForm.topic)
async def process_topic(message: types.Message, state: FSMContext):
    await state.update_data(topic=message.text)
    await message.answer("Universitet nomini kiriting (yoki 'Umumiy' deb yozing):")
    await state.set_state(CourseWorkForm.university)


@router.message(CourseWorkForm.university)
async def process_university(message: types.Message, state: FSMContext):
    await state.update_data(university=message.text)
    await message.answer("Sahifalar sonini kiriting (masalan, 20, 50, 70):")
    await state.set_state(CourseWorkForm.pages)


@router.message(CourseWorkForm.pages)
async def process_pages(message: types.Message, state: FSMContext):
    await state.update_data(pages=message.text)
    await message.answer("Tilni tanlang (uz, ru, en):")
    await state.set_state(CourseWorkForm.language)


@router.message(CourseWorkForm.language)
async def process_language(message: types.Message, state: FSMContext):
    await state.update_data(language=message.text)
    data = await state.get_data()

    # Backend’ga so‘rov yuborish
    response = requests.post(f"{BACKEND_URL}/api/courseworks/", json={
        "field": int(data["field"]),
        "topic": data["topic"],
        "university": data["university"],
        "pages": int(data["pages"]),
        "language": data["language"]
    })

    if response.status_code == 201:
        coursework_data = response.json()
        file_url = coursework_data.get("file")
        await message.answer("Kurs ishingiz tayyor! 📄 Yuklab olish uchun:")
        await message.answer(file_url)
    else:
        # Xato xabarini soddalashtirish
        await message.answer("Xatolik yuz berdi. Iltimos, qayta urinib ko‘ring yoki admin bilan bog‘laning.")

    await state.clear()
