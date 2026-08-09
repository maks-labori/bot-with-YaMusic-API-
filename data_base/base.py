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
                telegram_id_file TEXT UNIQUE,
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

async def add_track(track_id,id_from_users):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO tracks(track_id,id_from_users) VALUES(?,?)",(track_id,id_from_users))
        await db.commit()
