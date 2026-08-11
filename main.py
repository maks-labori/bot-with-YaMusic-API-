from aiogram import Dispatcher,Bot
import asyncio
from os import getenv
from dotenv import load_dotenv
from processing_message.router import router
from data_base.base import init_base
from yandex_music import ClientAsync

load_dotenv()
TOKEN = getenv("BOT_TOKEN")
KEY = getenv("YANDEX_TOKEN")

dp = Dispatcher()
dp.include_router(router)



@dp.startup()
async def start_client(dispatcher:Dispatcher):
    client = await ClientAsync(token = KEY).init()
    print(f"Привет,{client.me.account.first_name}")
    dispatcher['yandex_client'] = client

async def main():
    await init_base()
    bot = Bot(token=TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    print("Start")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())