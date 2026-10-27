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


TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
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

    today_key = datetime.now().strftime("%Y-%m-%d")
    day_signs_list = HOROSCOPES.get("days", {}).get(today_key, [])

    # Ищем объект с данными для выбранного знака
    sign_data = next((item for item in day_signs_list if item.get("signId") == sign_code), None)

    await callback.answer()

    if not sign_data:
        await callback.message.answer(
            f"К сожалению, гороскоп для знака {sign_name} на дату {today_key} не найден."
        )
        return

    # Достаем все нужные поля из найденного словаря
    headline = sign_data.get("headline", "")
    general_text = sign_data.get("generalText", "")
    love_rating = sign_data.get("loveRating", 0)
    love_tip = sign_data.get("loveTip", "")
    career_rating = sign_data.get("careerRating", 0)
    career_tip = sign_data.get("careerTip", "")
    lucky_number = sign_data.get("luckyNumber", "—")
    energy_color = sign_data.get("energyColor", "—")
    advice = sign_data.get("advice", "")

    # Превращаем числовые рейтинги (например, 4) в красивые звездочки: ⭐⭐⭐⭐☆
    love_stars = "⭐" * love_rating + "☆" * (5 - love_rating)
    career_stars = "⭐" * career_rating + "☆" * (5 - career_rating)

    # Собираем итоговое сообщение
    message_lines = [
        f"✨ {html.bold(sign_name)}",
    ]

    if headline:
        message_lines.append(f"📌 {html.italic(headline)}")

    if general_text:
        message_lines.append(f"\n{general_text}\n")

    # Блок сфер жизни
    message_lines.append(f"❤️ {html.bold('Любовь')}: {love_stars}")
    if love_tip:
        message_lines.append(f"└ {html.italic(love_tip)}")

    message_lines.append(f"\n💼 {html.bold('Карьера')}: {career_stars}")
    if career_tip:
        message_lines.append(f"└ {html.italic(career_tip)}")

    # Блок подсказок и удачи
    message_lines.append(f"\n🎲 {html.bold('Число дня')}: {lucky_number}")
    message_lines.append(f"🎨 {html.bold('Цвет энергии')}: {energy_color}")

    if advice:
        message_lines.append(f"\n💡 {html.bold('Совет дня')}: {advice}")

    # Объединяем все строки через перенос
    final_text = "\n".join(message_lines)

    # Создаем кнопку «Назад»
    back_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Выбрать другой знак", callback_data="back_to_signs")]
        ]
    )

    # Отправляем сообщение вместе с кнопкой
    await callback.message.answer(final_text, reply_markup=back_keyboard)


@dp.callback_query(F.data == "back_to_signs")
async def back_to_signs_handler(callback: CallbackQuery) -> None:
    await callback.answer()
    
    # Отправляем клавиатуру со всеми знаками (используем ту же функцию клавиатуры, что и в /start)
    await callback.message.answer(
        "Выберите знак зодиака:",
        reply_markup=get_zodiac_keyboard()
    )

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
