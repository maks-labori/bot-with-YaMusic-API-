from aiogram import Router,F
from aiogram.filters import Command
from aiogram.types import Message,BufferedInputFile,InlineKeyboardButton,callback_query,CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from data_base.base import add_user,add_track,check_track
import re
from yandex_music import ClientAsync

router = Router()

pattern = r'track/(\d+)'

COUNT_ANSWER = 5

async def download_track(yandex_id:str,yandex_client:ClientAsync):
    try:
        full_track = await yandex_client.tracks(yandex_id)
        if full_track:
            track_bytes = await full_track[0].download_bytes_async(codec="mp3")
            title = full_track[0].title
            artist = ",".join(list(map(lambda c:c.name,full_track[0].artists)))
            audio_file = BufferedInputFile(track_bytes,filename=f"{title}.mp3")
            track = {"audio":audio_file,"title":title,"artist":artist}
        else:return None
    except Exception as e:
        print(e)
        return None
    return track

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
            track_info = await check_track(int(yandex_id))
            if track_info:
                file_id = track_info[0]
                title = track_info[1]
                artist = track_info[2]
                await message.answer_audio(audio=file_id,title=title,performer=artist)
                return
            else:
                track = await download_track(yandex_id,yandex_client)
                if track:
                    send_message = await message.answer_audio(audio=track["audio"],title=track["title"],performer=track["artist"])
                    await add_track(int(yandex_id),send_message.audio.file_id,track["title"],track["artist"])
                else:
                    await message.answer("трек не нашелся")
        except Exception as e:
            await message.answer("сыллка битая или Яндекс лох")
            print(e)
        return
    try:
        res = await yandex_client.search(text = str(message.text),type_="track")    
        if res.tracks and res.tracks.results:
            full_tracks = list(res.tracks.results[:COUNT_ANSWER])
            if full_tracks: 
                builder = InlineKeyboardBuilder()
                for track in full_tracks:
                    builder.add(InlineKeyboardButton(text=f"{track.title} - {track.artists[0].name}",callback_data=f"id:{track.id}"))
                builder.adjust(1)
                await message.answer("Выберите вариант из предложенных",reply_markup=builder.as_markup())
            else: await message.answer("поиск сработал,но трек без полной версии(нельзя качать)")
        else:
            await message.answer("Поиск ничего не нашел")
    except Exception as e:
        await message.answer("Поиск лег или Яндекс лох")
        print(e)
    return

@router.callback_query(F.data[:3] == "id:")
async def download_inline(callback:CallbackQuery,yandex_client:ClientAsync):
    yandex_id = callback.data[3:]
    track_info = await check_track(int(yandex_id))
    if track_info:
        try:
            file_id = track_info[0]
            title = track_info[1]
            artist = track_info[2]
            await callback.message.answer_audio(audio=file_id,title=title,performer=artist)
        except:
            await callback.message.answer("Ошибка скачивания")
    else:
        try:
            track = await download_track(yandex_id,yandex_client)
        except:
            await callback.message.answer("Ошибка скачивания")
        if track:
            try:
                send_message = await callback.message.answer_audio(audio=track["audio"],title=track["title"],performer=track["artist"])
                await add_track(int(yandex_id),send_message.audio.file_id,track["title"],track["artist"])
            except Exception as e:
                await callback.message.answer("Ошибка отправки")
        else:
            await callback.message.answer("не нашелся трек")
    await callback.answer("")

    