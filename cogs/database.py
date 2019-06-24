import asyncio
import asyncpg
import random
import time


async def is_in_database(database, user_id):
    """Checks if a user is in the database.

    Arguments:
        database {var} -- The variable for the database.
        user_id {int} -- The Discord user ID to check.
    """
    row = await database.fetchrow("SELECT * FROM userinformation WHERE userid = $1", user_id)

    if row is None:
        await database.execute("INSERT INTO userinformation VALUES($1, $2, $3, $4, $5, $6, $7, $8)", user_id, 500, 0, [], [], [], False, False)


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


async def add_fakemon_to_database(database, owner_id, fakemon_name):
    """Adds a fakemon to the ownedfakemon database.

    Arguments:
        database {var} -- The variable for the database.
        owner_id {int} -- The Discord user ID to check.
        fakemon_name {str} -- The name of the fakemon to add.

    Returns:
        int -- The ID of the fakemon that just got added.
    """
    await database.execute('INSERT INTO ownedfakemon("ownerid", "name", "level", "xp", "moves", "iv") VALUES($1, $2, $3, $4, $5, $6) RETURNING fakemonid;', owner_id, fakemon_name, 5, 0, [], random.randint(1, 100))

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
