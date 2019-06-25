import asyncio
import asyncpg


async def get_random_fakemon(database):
    row = await database.fetchrow("SELECT * FROM allfakemon ORDER BY random() LIMIT 1;""")
    return row


async def get_fakemon(database, fakemon):
    row = await database.fetchrow("SELECT * FROM allfakemon WHERE name = $1", fakemon.capitalize())
    return row


async def get_fakemon_information(database, fakemon_id):
    row = await database.fetchrow("SELECT * FROM ownedfakemon WHERE fakemonid = $1", fakemon_id)
    return row


async def calculate_exp_needed(level):
    if level <= 50:
        return int((level ** 3 * (100 - level)) / 50)
    elif level <= 68:
        return int((level ** 3 * (150 - level)) / 100)
    elif level <= 98:
        return int((level ** 3 * ((1911 - 10 * level) / 3)) / 500)
    else:
        return int((level ** 3 * (160 - level)) / 100)
