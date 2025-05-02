from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_field_keyboard(fields):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=field["name"], callback_data=str(field["id"]))] for field in fields
    ])
    return keyboard
