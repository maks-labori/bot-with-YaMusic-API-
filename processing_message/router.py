from aiogram import Router,F
from aiogram.filters import Command
from aiogram.types import Message,BufferedInputFile,InlineKeyboardButton,InlineKeyboardMarkup,callback_query,CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from data_base.base import add_user,add_track,check_track,add_in_playlist,get_list_file,get_list_track,delete_track
import re
from yandex_music import ClientAsync
from aiogram.types.input_media_audio import InputMediaAudio
router = Router()

pattern = r'track/(\d+)'

COUNT_ANSWER = 5

user_buffer = set()

async def download_track(yandex_id:str,yandex_client:ClientAsync):
    try:
        full_track = await yandex_client.tracks(yandex_id)
        if full_track:
            track_bytes = await full_track[0].download_bytes_async(codec="mp3")
            title = full_track[0].title if full_track[0].title else "Без названия"
            artist = ",".join(list(map(lambda c:c.name,full_track[0].artists))) if full_track[0].artists else "Неизвестный исполнитель"
            audio_file = BufferedInputFile(track_bytes,filename=f"{title}.mp3") 
            year = full_track[0].albums[0].year if full_track[0].albums else 0
            track = {"audio":audio_file,"title":title,"artist":artist,"year":year}
        else:return None
    except Exception as e:
        print(e)
        return None
    return track

@router.message(Command("start"))
async def start_bot(message:Message):
    await message.answer(f"Привет,{message.from_user.first_name}!")
    await message.answer("Это бот для удобного скачивания и прослушивания твои любимых треков\n\nСписок того,что умеет бот:\n1) превратить ссылку на трек в файл\n2) после обычного текста представить список вариантов треков с таким названием для скачки\n3) /favourite_list - вывести список избранных треков\n4) /start - перезагрузить бота\n5) /delete - удалить песню из избранного\n6) Отправьте файл",parse_mode="HTML")
    await add_user(message.from_user.id,message.from_user.username)

@router.message(Command("favourite_list"))
async def print_list(message:Message):
    try:
        telegram_id = message.from_user.id
        track_list = await get_list_file(telegram_id)
        if not track_list:
            await message.answer("В избранном нету треков")
            return
        media_group = list(InputMediaAudio(media=x) for x in track_list)
        await message.answer_media_group(media=media_group)
    except Exception as e:
        await message.answer("Ошибка при выводе избранного")
        print(e)

@router.message(Command("delete"))
async def delete_command(message:Message):
    try:
        user_id = message.from_user.id
        list_track = await get_list_track(user_id)
        if not list_track:
            await message.answer("Список избранного пуст")
            return
        builder = InlineKeyboardBuilder()
        for track in list_track:
            yandex_id = track[0]
            title = track[1]
            artist = track[2]
            builder.add(InlineKeyboardButton(text=f"{title} - {artist}",callback_data=f"del:{yandex_id}"))
        builder.adjust(1)
        await message.answer("Нажмите на трек для удаления",reply_markup=builder.as_markup())
    except Exception as e:
        await message.answer("Ошибка при удалении")
        print(e)

@router.message(F.text)
async def processing(message:Message,yandex_client:ClientAsync):
    src = re.search(pattern,message.text)
    id = message.from_user.id
    if id in user_buffer:
        await message.answer("Не спамь,пожалуйста,бот выполняет команду")
        return
    if src:
        yandex_id = src.group()[6:]
        try:
            user_buffer.add(id)
            track_info = await check_track(int(yandex_id))
            if track_info:
                file_id = track_info[0]
                title = track_info[1]
                artist = track_info[2]
                year = f"{track_info[3]}г" if track_info[3] else ""
                await message.answer_audio(audio=file_id,title=title,performer=artist,caption=year,reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Текст песни",callback_data=f"text:{yandex_id}"),InlineKeyboardButton(text="В избранное",callback_data=f"add:{yandex_id}")]]))
                return
            else:
                track = await download_track(yandex_id,yandex_client)
                if track:
                    year = f"{track["year"]}г" if track["year"] else "" 
                    send_message = await message.answer_audio(audio=track["audio"],title=track["title"],performer=track["artist"],caption=year,reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Текст песни",callback_data=f"text:{yandex_id}"),InlineKeyboardButton(text="В избранное",callback_data=f"add:{yandex_id}")]]))
                    await add_track(int(yandex_id),send_message.audio.file_id,track["title"],track["artist"],track["year"])
                else:
                    await message.answer("трек не нашелся")
        except Exception as e:
            await message.answer("сыллка битая или Яндекс лох")
            print(e)
        finally:
            user_buffer.discard(id)
            return
    try:
        user_buffer.add(id)
        res = await yandex_client.search(text = str(message.text),type_="track")    
        if res.tracks and res.tracks.results:
            full_tracks = list(res.tracks.results[:COUNT_ANSWER])
            if full_tracks: 
                builder_list = InlineKeyboardBuilder()
                for track in full_tracks:
                    builder_list.add(InlineKeyboardButton(text=f"{track.title} - {track.artists[0].name}",callback_data=f"id:{track.id}"))
                builder_list.adjust(1)
                await message.answer("Выберите вариант из предложенных",reply_markup=builder_list.as_markup())
            else: await message.answer("поиск сработал,но трек без полной версии(нельзя качать)")
        else:
            await message.answer("Поиск ничего не нашел")
    except Exception as e:
        await message.answer("Поиск лег или Яндекс лох")
        print(e)
    finally:
        user_buffer.discard(id)
        return

@router.message(F.audio)
async def get_audio(message:Message):
    try:
        file_id = message.audio.file_id
        title = message.audio.title if message.audio.title else "Без навзания"
        artist = message.audio.performer if message.audio.performer else "Неизвестный исполнитель"
        fake_yandex_id = -(message.from_user.id)
        await add_track(fake_yandex_id,file_id,title,artist)
        await message.answer(text="Трек загружен",reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Добавить в плейлист",callback_data=f"add:{fake_yandex_id}")]]))
    except Exception as e:
        await message.answer("Ошибка при загрузке трека")
        print(e)

@router.callback_query(F.data[:3] == "id:")
async def download_inline(callback:CallbackQuery,yandex_client:ClientAsync):
    yandex_id = callback.data[3:]
    try:
        track_info = await check_track(int(yandex_id))
        if track_info:
            file_id = track_info[0]
            title = track_info[1]
            artist = track_info[2]
            year = f"{track_info[3]}г" if track_info[3] else ""
            await callback.message.answer_audio(audio=file_id,title=title,performer=artist,caption=year,reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Текст песни",callback_data=f"text:{yandex_id}"),InlineKeyboardButton(text="В избранное",callback_data=f"add:{yandex_id}")]]))
        else:
            track = await download_track(yandex_id,yandex_client)
            if track:
                year = f"{track["year"]}г" if track["year"] else ""
                send_message = await callback.message.answer_audio(audio=track["audio"],title=track["title"],performer=track["artist"],caption=year,reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Текст песни",callback_data=f"text:{yandex_id}"),InlineKeyboardButton(text="В избранное",callback_data=f"add:{yandex_id}")]]))
                await add_track(int(yandex_id),send_message.audio.file_id,track["title"],track["artist"],track["year"])
            else:
                await callback.message.answer("не нашелся трек")
    except Exception as e:
        await callback.message.answer("Ошибка скачивания")
        print(e)
    finally:
        await callback.answer("")

@router.callback_query(F.data[:5] == "text:")
async def give_text(callback:CallbackQuery,yandex_client:ClientAsync):
    try:
        yandex_id = callback.data[5:]
        track_info = await yandex_client.tracks_lyrics(yandex_id)
        if track_info:
            text = await track_info.fetch_lyrics_async()
            title = callback.message.audio.title if callback.message.audio else "Без названия"
            artist = callback.message.audio.performer if callback.message.audio else "Неизвестный исполнитель"
            year = callback.message.caption + "." if callback.message.caption else ""
            await callback.message.answer(f"{title}\nТрек - {artist} {year}\n\nТекст песни\n\n{text}")
    except Exception as e:
        await callback.message.answer("Текст песни не найден")
        print(e)
    finally:
        await callback.answer("")

@router.callback_query(F.data[:4] == "add:")
async def favourite_add(callback:CallbackQuery):
    try:
        yandex_id = callback.data[4:]
        user_id = callback.from_user.id
        flag = await add_in_playlist(yandex_id,user_id)
        if not flag:
            await callback.message.answer("Не нашлось такой песни/пользователя")
        elif flag == "full":
            await callback.message.answer("Лимит избранного 10 треков")
        else:
            await callback.message.answer("Трек добавлен")
    except Exception as e:
        await callback.message.answer("Ошибка при добавлении в избранное")
        print(e)
    finally:
        await callback.answer("")

@router.callback_query(F.data[:4] == "del:")
async def delete_track_callback(callback:CallbackQuery):
    try:
        yandex_id = callback.data[4:]
        user_id = callback.from_user.id
        await delete_track(user_id,yandex_id)
        await callback.message.answer("Трек удален")
    except Exception as e:
        await callback.message.answer("Ошибка при удалении")
        print(e)
    finally:
        await callback.answer("")