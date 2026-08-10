from aiogram import Router,F
from aiogram.filters import Command
from aiogram.types import Message,BufferedInputFile
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
                
                track_bytes = await full_track[0].download_bytes_async(codec="mp3")
                title = full_track[0].title
                artist = ",".join(list(map(lambda c:c.name,full_track[0].artists)))
                audio_file = BufferedInputFile(track_bytes,filename=f"{title}.mp3")
                await message.answer_audio(audio=audio_file,title=title,performer=artist)
        except Exception as e:
            await message.answer("сыллка битая или Яндекс лох")
            print(e)
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