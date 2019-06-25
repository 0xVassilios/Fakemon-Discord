import asyncio
import asyncpg
from cogs.database import *


async def get_random_fakemon(database):
    row = await database.fetchrow("SELECT * FROM allfakemon ORDER BY random() LIMIT 1;""")
    return row


async def get_fakemon(database, fakemon):
    row = await database.fetchrow("SELECT * FROM allfakemon WHERE name = $1", fakemon.capitalize())
    return row


async def get_fakemon_information(database, fakemon_id):
    row = await database.fetchrow("SELECT * FROM ownedfakemon WHERE fakemonid = $1", fakemon_id)
    return row


async def check_levelup(database, fakemon_id):
    fakemon = await get_fakemon_information(database=database, fakemon_id=fakemon_id)
    fakemon_information = await database.fetchrow('SELECT * FROM allfakemon WHERE name = $1', fakemon["name"])

    if fakemon["xp"] >= await calculate_exp_needed(fakemon["level"] + 1):
        exp = 0
        level = fakemon["level"] + 1
        evolved = False

        if level == fakemon_information["nextevolutionlevel"]:
            evolved = True
            name = fakemon_information["nextevolution"]

        await database.execute('UPDATE ownedfakemon SET level = $1 WHERE fakemonid = $2', level, fakemon_id)
        await database.execute('UPDATE ownedfakemon SET xp = $1 WHERE fakemonid = $2', exp, fakemon_id)

        if evolved:
            await database.execute('UPDATE ownedfakemon SET name = $1 WHERE fakemonid = $2', name, fakemon_id)


async def calculate_exp_needed(level):
    if level <= 50:
        return int((level ** 3 * (100 - level)) / 50)
    elif level <= 68:
        return int((level ** 3 * (150 - level)) / 100)
    elif level <= 98:
        return int((level ** 3 * ((1911 - 10 * level) / 3)) / 500)
    else:
        return int((level ** 3 * (160 - level)) / 100)
