import discord
from discord.ext import commands
from cogs.database import *


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(colour=0xDC143C)
        embed.add_field(
            name="Commands", value="""duel (user) : Duels another user in a predetermined category using your primary Fakemon.
equip (fakemon) : Equips a fakemon to be your primary one.
explore : Displays information about AFK exploring.
explore start (duration) : Starts AFK exploring.
explore status : Displays the remaining time for your exploration.
inventory : Displays information about your inventory.
inventory fakemon (page) : Displays all your current fakemon in pages.
inventory items (page) : Displays all your current items in pages.
inventory moves (page) : Displays all your current moves in pages.
money : Displays your money.
pay (user) (amount) : Pays another user.
pokedex (fakemon) : Displays information about said fakemon.
set location (event) (channel/category) [Admin Usage] : Sets the events to happen in location.
set [Admin Usage] : Dislays information about the set command.
shop : Displays all available items for purchase in the shop.
shop buy (item) : Buys an item from the shop.
starter : Displays all available starters.
starter choose (fakemon) : Chooses a fakemon as your starter.
stats (fakemon) : Displays the stats for an owned fakemon.
teach (fakemon) (move) : Teaches your selected Fakemon a move, if compatible.
trade (your fakemon) (user) (user's fakemon) : Trades Fakemon.""")


def setup(bot):
    bot.add_cog(Help(bot))
