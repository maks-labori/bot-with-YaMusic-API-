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
    await init_base()
    bot = Bot(token=TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    print("Start")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())