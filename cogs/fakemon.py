from cogs.database import *
import aiohttp
import asyncio
import asyncpg
import json


async def get_random_fakemon(database):
    """Retrieves a random Fakemon from the database.

    Arguments:
        database {var} -- The variable for the database.
    """
    row = await database.fetchrow("SELECT * FROM allfakemon ORDER BY random() LIMIT 1;""")
    return row


async def get_fakemon(database, fakemon):
    """Retrieves a selected Fakemon from the database.

    Arguments:
        database {var} -- The variable for the database.
        fakemon {str} -- The name of the fakemon you want to find.
    """
    row = await database.fetchrow("SELECT * FROM allfakemon WHERE name = $1", fakemon.capitalize())
    return row


async def get_fakemon_information(database, fakemon_id):
    """Retrieves the information of an owned Fakemon from the database.

    Arguments:
        database {var} -- The variable for the database.
        fakemon_id {int} -- The ID of the fakemon that you want to find.
    """
    row = await database.fetchrow("SELECT * FROM ownedfakemon WHERE fakemonid = $1", fakemon_id)
    return row


async def check_levelup(database, fakemon_id):
    """This function checks if the selected fakemon can level up or evolve.

    Arguments:
        database {var} -- The variable for the database.
        fakemon_id {int} -- The ID of the fakemon that you want to check.
    """
    fakemon = await get_fakemon_information(database=database, fakemon_id=fakemon_id)
    fakemon_information = await database.fetchrow('SELECT * FROM allfakemon WHERE name = $1', fakemon["name"])

    while fakemon["xp"] >= await calculate_exp_needed(fakemon["level"] + 1):
        exp_needed = await calculate_exp_needed(fakemon["level"] + 1)
        exp = fakemon["xp"] - exp_needed
        level = fakemon["level"] + 1
        evolved = False

        if level == fakemon_information["nextevolutionlevel"]:
            evolved = True
            name = fakemon_information["nextevolution"]

        await database.execute('UPDATE ownedfakemon SET level = $1 WHERE fakemonid = $2', level, fakemon_id)
        await database.execute('UPDATE ownedfakemon SET xp = $1 WHERE fakemonid = $2', exp, fakemon_id)

        if evolved:
            await database.execute('UPDATE ownedfakemon SET name = $1 WHERE fakemonid = $2', name, fakemon_id)

        fakemon = await get_fakemon_information(database=database, fakemon_id=fakemon_id)


async def calculate_exp_needed(level):
    """Calculates the total EXP needed for a level of your choice.

    Arguments:
        level {int} -- The level you want to check.
    """
    if level <= 50:
        return int((level ** 3 * (100 - level)) / 50)
    elif level <= 68:
        return int((level ** 3 * (150 - level)) / 100)
    elif level <= 98:
        return int((level ** 3 * ((1911 - 10 * level) / 3)) / 500)
    else:
        return int((level ** 3 * (160 - level)) / 100)


async def get_battle_information(database, user, enemy):
    """Gets a dictionary of the information of both Fakemon.

    Arguments:
        database {var} -- The variable for the database.
        user {int} -- The ID of player one's Fakemon.
        enemy {int} -- The ID of player two's Fakemon.
    """

    def calculate_hp(level, iv):
        """It calculates the maximum HP of a user.

        Arguments:
            level {int} -- The level of the Fakemon.
            iv {int} -- The IV of the Fakemon.

        Returns:
            int -- The value of the calculation.
        """
        return int((iv + 2 + 200 * level) / 100) + 10

    # We retrieve the Pokedex in JSON.
    with open("pokedex.json", "r", encoding="UTF8") as file:
        pokedex = json.load(file)

    user_info = await database.fetchrow("SELECT * FROM userinformation WHERE userid = $1", user)
    enemy_info = await database.fetchrow("SELECT * FROM userinformation WHERE userid = $1", enemy)

    # If either of the users don't have a Fakemon then we return False.
    if user_info["primaryfakemon"] == 0 or enemy_info["primaryfakemon"] == 0:
        return False

    # We retrieve the information and place it in a dictionary which we return.
    user_fakemon = await get_fakemon_information(database=database, fakemon_id=user_info["primaryfakemon"])
    enemy_fakemon = await get_fakemon_information(database=database, fakemon_id=enemy_info["primaryfakemon"])

    battle_db = {
        "User": {
            "Name": user_fakemon["name"],
            "Level": user_fakemon["level"],
            "HP": calculate_hp(user_fakemon["level"], user_fakemon["iv"]),
            "Max HP": calculate_hp(user_fakemon["level"], user_fakemon["iv"]),
            "Moves": user_fakemon["moves"],
            "Sprite": pokedex[user_fakemon["name"]]["Image URL"]
        },
        "Enemy": {
            "Name": enemy_fakemon["name"],
            "Level": enemy_fakemon["level"],
            "HP": calculate_hp(enemy_fakemon["level"], enemy_fakemon["iv"]),
            "Max HP": calculate_hp(enemy_fakemon["level"], enemy_fakemon["iv"]),
            "Moves": enemy_fakemon["moves"],
            "Sprite": pokedex[enemy_fakemon["name"]]["Image URL"]
        }
    }

    return battle_db
