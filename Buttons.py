from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

menu_kb = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="Голосовое общение🗣"),
        KeyboardButton(text="Текстовое общение📝")
    ],
    [
        KeyboardButton(text="Вся переписка"),
    ],
], resize_keyboard=True)
