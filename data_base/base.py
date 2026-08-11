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
                artist_name TEXT
            )
                        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS favorite_tracks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id INTEGER,
                id_from_users INTEGER,
                FOREIGN KEY (id_from_users) REFERENCES users (user_id)
                FOREIGN KEY (track_id) REFERENCES track_base (id)
            )
                        """)
        await db.commit()

async def add_user(user_id,username = "NULL"):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO users(user_id,username) SELECT ?,? WHERE NOT EXISTS(SELECT 1 FROM users WHERE user_id = ?)",(user_id,username,user_id))
        await db.commit()

async def add_track(yandex_id_file,file_id,track_name,artist_name):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO track_base(yandex_id_file,file_id,track_name,artist_name) SELECT ?,?,?,? WHERE NOT EXISTS(SELECT 1 FROM track_base WHERE yandex_id_file = ?)",(yandex_id_file,file_id,track_name,artist_name,yandex_id_file))
        await db.commit()

async def check_track(yandex_id_file):
    async with aiosqlite.connect(DB_NAME) as db:
        object = await db.execute("SELECT file_id,track_name,artist_name FROM track_base WHERE yandex_id_file = ?",(yandex_id_file,))
        track_info = await object.fetchone()
        return track_info