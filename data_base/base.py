import aiosqlite

DB_NAME = "data_base.sql"

async def init_base():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTGER PRIMARY KEY AUTOINCREMENT
                user_id INTEGER
            )
                    """) 
        await db.commit()

async def add_user(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO users(user_id) VALUES(?)",(user_id))
        await db.commit()
