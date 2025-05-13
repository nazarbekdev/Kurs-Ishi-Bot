from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🎓 Kurs ishi"),
            KeyboardButton(text="📄 Mustaqil ish")
        ],
        [
            KeyboardButton(text="💰 Balans"),
            KeyboardButton(text="🔖 Tariflar")
        ],
        [
            KeyboardButton(text="🎲 Sirli Kupon")
        ]
    ],
    resize_keyboard=True
)

confirm_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Ha"), KeyboardButton(text="Yo'q")],
], resize_keyboard=True)

language_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="O'zbekcha"), KeyboardButton(text="Ruscha"), KeyboardButton(text="Inglizcha")],
], resize_keyboard=True)

tariff_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Tariflar")],
], resize_keyboard=True)
