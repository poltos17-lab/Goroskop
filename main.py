import asyncio
import json
import logging
import sys
import os
from datetime import datetime
from configparser import ConfigParser

from aiogram import Bot, Dispatcher, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message



dp = Dispatcher()

# 1. Загружаем гороскопы из файла при старте программы
with open("horoscopes.json", "r", encoding="utf-8") as f:
    HOROSCOPES = json.load(f)

ZODIAC_SIGNS = [
    ("aries", "Овен ♈"),
    ("taurus", "Телец ♉"),
    ("gemini", "Близнецы ♊"),
    ("cancer", "Рак ♋"),
    ("leo", "Лев ♌"),
    ("virgo", "Дева ♍"),
    ("libra", "Весы ♎"),
    ("scorpio", "Скорпион ♏"),
    ("sagittarius", "Стрелец ♐"),
    ("capricorn", "Козерог ♑"),
    ("aquarius", "Водолей ♒"),
    ("pisces", "Рыбы ♓"),
]


def get_zodiac_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for i in range(0, len(ZODIAC_SIGNS), 2):
        row = [
            InlineKeyboardButton(
                text=ZODIAC_SIGNS[i][1],
                callback_data=f"sign_{ZODIAC_SIGNS[i][0]}",
            ),
            InlineKeyboardButton(
                text=ZODIAC_SIGNS[i + 1][1],
                callback_data=f"sign_{ZODIAC_SIGNS[i + 1][0]}",
            ),
        ]
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user_name = message.from_user.first_name
    welcome_text = (
        f"Привет, {html.bold(user_name)}! 👋\n\n"
        "Я бот-предсказатель. Я могу показать твой персональный гороскоп на сегодня.\n\n"
        "Выбери свой знак зодиака 👇"
    )
    await message.answer(welcome_text, reply_markup=get_zodiac_keyboard())


# 2. Обработчик нажатия на знак зодиака
@dp.callback_query(F.data.startswith("sign_"))
async def process_zodiac_choice(callback: CallbackQuery) -> None:
    sign_code = callback.data.split("_")[1]
    sign_name = next(name for code, name in ZODIAC_SIGNS if code == sign_code)

    # Получаем текущую дату в формате "MM-DD" (например, "09-01")
    today_key = datetime.now().strftime("%m-%d")

    # Достаем гороскоп для выбранного знака на сегодня
    today_horoscope = HOROSCOPES.get(today_key, {}).get(
        sign_code, 
        "К сожалению, гороскоп на сегодня не найден."
    )

    await callback.answer()

    response_text = (
        f"✨ {html.bold(sign_name)} — Гороскоп на сегодня:\n\n"
        f"{today_horoscope}"
    )

    await callback.message.answer(response_text)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
