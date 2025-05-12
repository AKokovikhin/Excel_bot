import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import Update
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv
import openai

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)

PROMPT_TEMPLATE = """
Ты — помощник по Microsoft Excel и Google Таблицам.
Пользователь задал вопрос: "{}"
Ответь кратко, ясно и, если нужно, приведи формулы.
"""


@dp.message(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот-помощник по Excel и Google Таблицам.\nПросто напиши, что ты хочешь сделать, и я постараюсь помочь!")


@dp.message()
async def handle_message(message: types.Message):
    question = message.text.strip()
    prompt = PROMPT_TEMPLATE.format(question)
    await message.answer("🤔 Думаю...")

    try:
        response = openai.chat.completions.create(
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


async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(bot: Bot):
    await bot.delete_webhook()


def main():
    app = web.Application()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))


if __name__ == "__main__":
    main()
