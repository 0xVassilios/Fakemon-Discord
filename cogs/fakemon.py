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
