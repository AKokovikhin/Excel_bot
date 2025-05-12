import openai
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ParseMode
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# Настройка логов
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)

PROMPT_TEMPLATE = """
Ты — помощник по Microsoft Excel и Google Таблицам.
Пользователь задал вопрос: "{}"
Ответь кратко, ясно и, если нужно, приведи формулы.
"""

# Обработчик команды /start


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "Привет! Я бот-помощник по Excel и Google Таблицам.\n"
        "Просто напиши, что ты хочешь сделать, и я постараюсь помочь!"
    )

# Обработчик текстовых сообщений


@dp.message_handler()
async def handle_message(message: types.Message):
    question = message.text.strip()
    prompt = PROMPT_TEMPLATE.format(question)

    await message.answer("🤔 Думаю...")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=400
        )
        reply = response.choices[0].message.content.strip()
        await message.answer(reply)
    except Exception as e:
        logging.exception(e)
        await message.answer("⚠️ Произошла ошибка при обращении к OpenAI. Попробуй позже.")

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
