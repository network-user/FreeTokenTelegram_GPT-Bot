import asyncio

from g4f.client import AsyncClient
from g4f.Provider import Aichatos

from aiogram import (Router, Bot, Dispatcher,
                     F, types)
import logging

# Укажите имя для логгера и роутера
name = "my_bot"
router = Router(name=name)
lock = asyncio.Lock()

logger = logging.getLogger(name)
logging.basicConfig(level=logging.INFO)

# Функция для взаимодействия с GPT
async def response_gpt(message):
    client = AsyncClient(provider=Aichatos)

    try:
        completion = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=message,
        )
        return completion.choices[0].message.content

    except Exception as ex:
        print(ex)
        return None

# Обработчик сообщений в обычных чатах
@router.message(F.text)
async def handler_message(message: types.Message):
    async with lock:
        user_id = message.chat.id
        logger.info(f"Received message from {user_id}: {message.text}")
        # Задать промпт для начального взаимодействия
        messages = [
            {"role": "system", "content": "Привет! Ты - ИИ-помощник для пользователей в Telegram. Отвечай на вопросы пользователей"},
            {"role": "user", "content": message.text}
        ]

        response = await response_gpt(messages)

        if response is None:
            await message.answer("Я не понимаю вас. Попробуй еще раз.")
        else:
            logger.info(f"Response sent to chat: {response}")
            await message.answer(response)

# Основная функция для запуска бота
async def main() -> None:
    bot = Bot(token="TOKEN") # Указываете свой токен от Телеграм бота
    dp = Dispatcher()

    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())
