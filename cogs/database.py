import asyncio
import asyncpg
import random


async def is_in_database(database, user_id):
    row = await database.fetchrow("SELECT * FROM userinformation WHERE userid = $1", user_id)

    if row is None:
        await database.execute("INSERT INTO userinformation VALUES($1, $2, $3, $4, $5, $6, $7, $8)", user_id, 500, 0, [], [], [], False, False)


async def get_user_information(database, user_id):
    await is_in_database(database=database, user_id=user_id)
    row = await database.fetchrow("SELECT * FROM userinformation WHERE userid = $1", user_id)
    return row


async def add_fakemon_to_database(database, owner_id, fakemon_name):
    await is_in_database(database=database, user_id=owner_id)
    await database.execute('INSERT INTO ownedfakemon("ownerid", "name", "level", "xp", "moves", "iv") VALUES($1, $2, $3, $4, $5, $6) RETURNING fakemonid;', owner_id, fakemon_name, 5, 0, [], random.randint(1, 100))

    fakemon_id = await database.fetchrow('SELECT fakemonid FROM ownedfakemon ORDER BY fakemonid DESC LIMIT 1')

    return fakemon_id["fakemonid"]


async def add_fakemon_to_inventory(database, owner_id, fakemon_id):
    await is_in_database(database=database, user_id=owner_id)

    user = await get_user_information(database=database, user_id=owner_id)

    if user["fakemoninventory"] == []:
        inventory = [int(fakemon_id)]
    else:
        inventory = user["fakemoninventory"]
        inventory.append(fakemon_id)

    await database.execute('UPDATE userinformation SET fakemoninventory = $1 WHERE userid = $2', inventory, owner_id)
