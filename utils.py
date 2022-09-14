import databases
from database import DB_URL


async def check_db_connected():
    try:
        database = databases.Database(DB_URL)
        if not database.is_connected:
            await database.connect()
        # print("Database is connected")
    except Exception as e:
       # print("Looks like there is some problem in connection")
       raise e
