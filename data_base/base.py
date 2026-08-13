import aiosqlite

DB_NAME = "data_base.sql"

async def init_base():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                username TEXT
            )
                        """) 
        await db.execute("""
            CREATE TABLE IF NOT EXISTS track_base(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                yandex_id_file INTEGER UNIQUE,
                file_id TEXT UNIQUE,
                track_name TEXT,
                artist_name TEXT,
                year INTEGER
            )
                        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS favorite_tracks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id INTEGER,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (track_id) REFERENCES track_base (id)
            )
                        """)
        await db.commit()

async def add_user(user_id,username = "NULL"):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO users(user_id,username) SELECT ?,? WHERE NOT EXISTS(SELECT 1 FROM users WHERE user_id = ?)",(user_id,username,user_id))
        await db.commit()

async def add_track(yandex_id_file,file_id,track_name,artist_name,year = 0):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO track_base(yandex_id_file,file_id,track_name,artist_name,year) SELECT ?,?,?,?,? WHERE NOT EXISTS(SELECT 1 FROM track_base WHERE yandex_id_file = ?)",(yandex_id_file,file_id,track_name,artist_name,year,yandex_id_file))
        await db.commit()

async def check_track(yandex_id_file):
    async with aiosqlite.connect(DB_NAME) as db:
        object = await db.execute("SELECT file_id,track_name,artist_name,year FROM track_base WHERE yandex_id_file = ?",(yandex_id_file,))
        track_info = await object.fetchone()
        return track_info

async def add_in_playlist(yandex_id,telegram_id):
    async with aiosqlite.connect(DB_NAME) as db:
        object_1 = await db.execute("SELECT id FROM users WHERE user_id = ?",(telegram_id,))
        object_2 = await db.execute("SELECT id FROM track_base WHERE yandex_id_file = ?",(yandex_id,))
        user_row = await object_1.fetchone()
        track_row = await object_2.fetchone()
        if not user_row or not track_row:
            return None
        user_id = user_row[0]
        track_id = track_row[0]
        is_check = await db.execute("SELECT count(track_id) FROM favorite_tracks WHERE user_id = ? ",(user_id,))
        if (await is_check.fetchone())[0] >= 10:
            return "full"
        cursor = await db.execute("SELECT 1 FROM favorite_tracks WHERE track_id = ? AND user_id = ?",(track_id,user_id))
        if await cursor.fetchone():
            await db.execute("DELETE FROM favorite_tracks WHERE track_id = ? AND user_id = ?",(track_id,user_id))
            await db.commit()
        await db.execute("INSERT INTO favorite_tracks(track_id,user_id) VALUES(?,?)",(track_id,user_id))
        await db.commit()
        return True

async def get_list_file(telegram_id):
    async with aiosqlite.connect(DB_NAME) as db:
        sql = await db.execute("SELECT track_base.file_id FROM track_base " \
        "JOIN favorite_tracks ON track_base.id = favorite_tracks.track_id " \
        "JOIN users ON favorite_tracks.user_id = users.id " \
        "WHERE users.user_id = ? " \
        "ORDER BY favorite_tracks.id DESC",(telegram_id,)) 
        list_id = await sql.fetchall()
        return [x[0] for x in list_id]

async def get_list_track(telegram_id):
    async with aiosqlite.connect(DB_NAME) as db:
        sql = await db.execute("SELECT track_base.yandex_id_file,track_base.track_name,track_base.artist_name FROM track_base " \
                "JOIN favorite_tracks ON track_base.id = favorite_tracks.track_id " \
                "JOIN users ON favorite_tracks.user_id = users.id " \
                "WHERE users.user_id = ? " \
                "ORDER BY favorite_tracks.id DESC",(telegram_id,)) 
        track_list = await sql.fetchall()
        return track_list

async def delete_track(telegram_id,yandex_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM favorite_tracks " \
        "WHERE favorite_tracks.user_id = (SELECT users.id FROM users WHERE users.user_id = ?) " \
        "AND favorite_tracks.track_id = (SELECT track_base.id FROM track_base WHERE track_base.yandex_id_file = ?)",(telegram_id,int(yandex_id)))
        await db.commit()