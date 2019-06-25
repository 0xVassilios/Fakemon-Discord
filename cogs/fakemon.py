import asyncio
import asyncpg
from cogs.database import *
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import random
import requests
import json
from io import BytesIO


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


async def generate_battle_scene(one_name, one_level, one_hp, one_max_hp, two_name, two_level, two_hp, two_max_hp):
    with open("pokedex.json", "r", encoding="UTF8") as file:
        pokedex = json.load(file)

    battle_scene = Image.open("cogs/battlescene.png")

    one_hp_bar = Image.open(f"hp_bars/{one_hp}.png")
    one_sprite = Image.open(BytesIO(requests.get(
        pokedex[one_name]["Image URL"]).content))
    one_sprite.thumbnail((150, 150))

    two_hp_bar = Image.open(f"hp_bars/{two_hp}.png")
    two_sprite = Image.open(
        BytesIO(requests.get(pokedex[two_name]["Image URL"]).content))
    two_sprite.thumbnail((150, 150))

    # Health bars
    battle_scene.paste(one_hp_bar, (31, 39), mask=one_hp_bar)
    battle_scene.paste(two_hp_bar, (315, 171), mask=two_hp_bar)

    # Sprites
    battle_scene.paste(one_sprite, (74, 105), mask=one_sprite)
    battle_scene.paste(two_sprite, (343, 8), mask=two_sprite)

    # Names
    draw = ImageDraw.Draw(battle_scene)
    font = ImageFont.truetype('cogs/battlefont.ttf', 25)
    draw.text(
        (41, 44), f"{one_name}", (0, 0, 0), font=font)
    draw.text(
        (323, 176), f"{two_name}", (0, 0, 0), font=font)

    # Levels
    font = ImageFont.truetype('cogs/battlefont.ttf', 25)
    draw.text(
        (158, 49), f"Level  {one_level}", (0, 0, 0), font=font)
    draw.text(
        (442, 182), f"Level  {two_level}", (0, 0, 0), font=font)

    # Health Text
    font = ImageFont.truetype('cogs/battlefont.ttf', 25)
    draw.text(
        (132, 87), f"HP: {one_hp[1:]}/{one_max_hp}", (0, 0, 0), font=font)
    draw.text(
        (415, 220), f"HP: {two_hp[1:]}/{two_max_hp}", (0, 0, 0), font=font)

    return battle_scene
