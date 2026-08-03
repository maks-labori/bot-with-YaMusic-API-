from aiogram import Dispatcher,Bot
import asyncio
from os import getenv
from dotenv import load_dotenv
from processing_message.router import router
from data_base.base import init_base

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()
dp.include_router(router)

async def main():
    bot = Bot(token=TOKEN)
    print("Start")
    await dp.start_polling(bot)

if __name__ == "main.py":
    asyncio.run(main())