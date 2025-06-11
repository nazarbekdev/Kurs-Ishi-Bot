from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🎓 Kurs ishi"),
            KeyboardButton(text="📄 Mustaqil ish")
        ],
        [
            KeyboardButton(text="🚀 Maxsus Kurs Ishi"),
            KeyboardButton(text="📕 Slayd Tayyorlash")
        ],
        [
            KeyboardButton(text="💰 Balans"),
            KeyboardButton(text="🎲 Sirli Kupon")
        ],
        [
            KeyboardButton(text="🔖 Tariflar"),
            KeyboardButton(text="📘 Qo'llanma")
        ],
        [
            KeyboardButton(text="👨‍💻 Admin")
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
