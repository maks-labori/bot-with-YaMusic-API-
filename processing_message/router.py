from aiogram import Router,F
from aiogram.filters import Command
from aiogram.types import Message
from data_base.base import add_user
import re
from yandex_music import ClientAsync

router = Router()

pattern = r'track/(\d+)'

COUNT_ANSWER = 5

@router.message(Command("start"))
async def start_bot(message:Message):
    await message.answer(f"Привет,{message.from_user.first_name}\nЭто бот для удобного скачивания и прослушивания твои любимых треков\nОтправь мне ссылку на трек с яндекс музыки или напиши примерное название")
    await add_user(message.from_user.id,message.from_user.username)
    await message.answer("Извините,бот пока не работает,сохраните его где-нибудь,я обещаю сделать его,стараюсь каждый день,можете лично написать\n@maksggg_bs")

@router.message(F.text)
async def processing(message:Message,yandex_client:ClientAsync):
    src = re.search(pattern,message.text)

    if src:
        yandex_id = src.group()[6:]
        try:
            full_track = await yandex_client.tracks(yandex_id)
            if full_track:
                await message.answer(f"Вы отправвили ссылку на трек - {full_track[0].title}")
        except:
            await message.answer("сыллка битая или Яндекс лох")
        return
    try:
        res = await yandex_client.search(text = str(message.text),type_="track")    
        if res.tracks and res.tracks.results:
            full_track = list(res.tracks.results[:COUNT_ANSWER])
            if full_track: await message.answer(f"Самый подходящий вариант поиска - {full_track[0].title}")
            else: await message("поиск сработал,но трек без полной версии(нельзя качать)")
        else:
            await message.answer("Поиск ничего не нашел")
    except:
        await message.answer("Поиск лег или Яндекс лох")
    return