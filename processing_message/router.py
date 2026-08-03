from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from data_base.base import add_user
router = Router()

@router.message(Command("start"))
async def start_bot(message:Message):
    await message.answer(f"Привет,{message.from_user.first_name}\nЭто бот для удобного скачивания и прослушивания твои любимых треков\nОтправь мне ссылку на трек с яндекс музыки или напиши примерное название")
    