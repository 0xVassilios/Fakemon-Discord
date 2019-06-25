import asyncio
import asyncpg
import random
import time
from cogs.fakemon import get_fakemon_information, calculate_exp_needed


async def is_in_database(database, user_id):
    """Checks if a user is in the database.

    Arguments:
        database {var} -- The variable for the database.
        user_id {int} -- The Discord user ID to check.
    """
    row = await database.fetchrow("SELECT * FROM userinformation WHERE userid = $1", user_id)

    if row is None:
        await database.execute("INSERT INTO userinformation VALUES($1, $2, $3, $4, $5, $6, $7, $8)", user_id, 500, 0, [], [], [], False, False)


async def is_guild_in_database(database, server_id):
    """Checks if a guild is in the database.

    Arguments:
        database {var} -- The variable for the database.
        server_id {int} -- The ID of the targetted server.
    """
    row = await database.fetchrow("SELECT * FROM channels WHERE server = $1", server_id)

    if row is None:
        await database.execute("INSERT INTO channels VALUES($1, $2, $3)", server_id, 0, 0)


async def get_user_information(database, user_id):
    """Gets all the information for a user from the database.

    Arguments:
        database {var} -- The variable for the database.
        user_id {int} -- The Discord user ID to check.

    Returns:
        row -- All the information from the database's row.
    """
    row = await database.fetchrow("SELECT * FROM userinformation WHERE userid = $1", user_id)
    return row


async def add_fakemon_to_database(database, owner_id, fakemon_name, starter):
    """Adds a fakemon to the ownedfakemon database.

    Arguments:
        database {var} -- The variable for the database.
        owner_id {int} -- The Discord user ID to check.
        fakemon_name {str} -- The name of the fakemon to add.
        starter {boolean} -- Checks if it's the starter pokemon.

    Returns:
        int -- The ID of the fakemon that just got added.
    """
    if starter is True:
        level = 5
        xp = 0
    else:
        level = random.randint(5, 51)
        xp_needed = await calculate_exp_needed(level=level)
        xp = random.randint(0, level + 1)

    await database.execute('INSERT INTO ownedfakemon("ownerid", "name", "level", "xp", "moves", "iv") VALUES($1, $2, $3, $4, $5, $6) RETURNING fakemonid;', owner_id, fakemon_name, level, xp, [], random.randint(1, 100))

    fakemon_id = await database.fetchrow('SELECT fakemonid FROM ownedfakemon ORDER BY fakemonid DESC LIMIT 1')

    return fakemon_id["fakemonid"]


async def add_fakemon_to_inventory(database, owner_id, fakemon_id):
    """Adds a fakemon to a user's inventory.

    Arguments:
        database {var} -- The variable for the database.
        owner_id {int} -- The ID of the owner of the fakemon.
        fakemon_id {int} -- The ID of the fakemon.
    """
    user = await get_user_information(database=database, user_id=owner_id)

    if user["fakemoninventory"] == []:
        inventory = [int(fakemon_id)]
    else:
        inventory = user["fakemoninventory"]
        inventory.append(fakemon_id)

    await database.execute('UPDATE userinformation SET fakemoninventory = $1 WHERE userid = $2', inventory, owner_id)


async def is_in_adventure(database, user_id):
    """Checks if a user is in an adventure.

    Arguments:
        database {var} -- The variable for the database.
        user_id {int} -- The ID of the user.

    Returns:
        boolean -- True if in an adventure otherwise False.
    """
    row = await database.fetchrow('SELECT * FROM adventures WHERE userid = $1', user_id)

    if row is None:
        return False
    else:
        return True


async def add_adventure(database, user_id, duration):
    """Adds someone in an adventure.

    Arguments:
        database {var} -- The variable for the database.
        user_id {int} -- The ID of the user.
        duration {int} -- The duration of the adventure in minutes.
    """
    await database.execute('INSERT INTO adventures VALUES($1, $2, $3)', user_id, time.time(), duration * 60)


async def remove_adventure(database, user_id):
    """Removes the adventure from the database.

    Arguments:
        database {var} -- The variable for the database.
        user_id {int} -- The ID of the user whose adventure ended.
    """
    await database.execute('DELETE FROM adventures WHERE userid = $1', user_id)


async def get_adventure_information(database, user_id):
    """Retrieves the information about the adventure.

    Arguments:
        database {var} -- The variable for the database.
        user_id {int} -- The ID of the user.

    Returns:
        row -- All the information from the database's row.
    """
    row = await database.fetchrow('SELECT * FROM adventures WHERE userid = $1', user_id)
    return row


async def give_money(database, user_id, amount):
    """Gives a specified amount of money to a user.

    Arguments:
        database {var} -- The variable for the database.
        user_id {int} -- The ID of the user that will receive the money.
        amount {int} -- Amount of money earned.
    """
    user = await get_user_information(database=database, user_id=user_id)

    current_money = user["money"]
    current_money += amount

    await database.execute('UPDATE userinformation SET money = $1 WHERE userid = $2', current_money, user_id)


async def give_xp_to_fakemon(database, user_id, amount):
    """Gives a certain amount of XP to a fakemon.

    Arguments:
        database {var} -- The variable for the database.
        user_id {int} -- The ID of the user who owns the fakemon.
        amount {int} -- The amount of XP gained.
    """
    user = await get_user_information(database=database, user_id=user_id)

    if user["primaryfakemon"] != 0:
        fakemon = await get_fakemon_information(database=database, fakemon_id=user["primaryfakemon"])

        current_xp = fakemon["xp"]
        current_xp += amount

        await database.execute('UPDATE ownedfakemon SET xp = $1 WHERE fakemonid = $2', current_xp, user["primaryfakemon"])


async def get_random_question(database):
    row = await database.fetchrow("SELECT * FROM trivia ORDER BY random() LIMIT 1;""")

    return row["question"], row["answer"]
