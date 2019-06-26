import discord
from discord.ext import commands
import asyncio
import asyncpg
import traceback
import sys
import json
from cogs.database import is_in_database, is_guild_in_database
from discord.ext.commands import CommandNotFound

with open("passwords.json", "r", encoding="UTF8") as file:
    passwords = json.load(file)

bot = commands.Bot(command_prefix="f!")
bot.remove_command('help')


@bot.event
async def on_ready():
    print(
        f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    print(f'Successfully logged in and booted...!')
    await bot.change_presence(activity=discord.Game(name='with other Fakemon!'))


@bot.event
async def on_message(message):
    await is_in_database(database=bot.db, user_id=message.author.id)
    await is_guild_in_database(database=bot.db, server_id=message.guild.id)
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error


async def run():
    credentials = {"user": "postgres", "password": passwords["database"],
                   "database": "fakemon", "host": "127.0.0.1"}

    db = await asyncpg.create_pool(**credentials)

    bot.db = db

    try:
        await bot.start(passwords["bot"])
    except KeyboardInterrupt:
        await bot.logout()

initial_extensions = ['cogs.pokedex', 'cogs.starters',
                      'cogs.adventures', 'cogs.locations', 'cogs.wildfakemon', 'cogs.inventory', 'cogs.shop', 'cogs.trade', 'cogs.learn_moves', 'cogs.misc', 'cogs.duels', 'cogs.help']

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

bot.all_starters_list = ["Cuboo", "Sizzabre", "Platyke", "Limbetaur", "Jersinge", "Quendro", "Dinaut", "Coalidi", "Camodden", "Cuberry", "Wyburn", "Glaucute", "Shrubria", "Walpyre", "Pakisea", "Kumizar", "Duikin", "Barkrest", "Seedrake", "Balmox", "Shtryke",
                         "Chidrupe", "Shelight", "Squirtama", "Coltivus", "Aspyre", "Soakitt", "Sweetyke", "Frisun", "Cresshor", "Belladino", "Whelpyre", "Bubbrine", "Galeaf", "Elephlint", "Creeklaw", "Kitnip", "Lutred", "Kalflow", "Anamary", "Charret", "Swinerve"]

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
