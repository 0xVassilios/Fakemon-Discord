import discord
from discord.ext import commands
from cogs.fakemon import get_fakemon
from cogs.database import is_in_database, add_fakemon_to_database, get_user_information, add_fakemon_to_inventory


class Starters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def starters(self, ctx):
        all_starters = "\n".join(self.bot.all_starters_list)

        embed = discord.Embed(title="All Starters Available", colour=0xDC143C)
        embed.add_field(
            name="You may use your pokedex to investigate any of the starters.", value=all_starters)
        embed.set_footer(
            text="Use 'f!starter choose (fakemon)' to choose your starter!")
        await ctx.send(embed=embed)

    @starters.command()
    async def choose(self, ctx, *, fakemon_name: str):
        user = await get_user_information(database=self.bot.db, user_id=ctx.author.id)

        if user["starter"] is True:
            embed = discord.Embed(
                title=f"You have already received a starter!", colour=0xDC143C)
            await ctx.send(embed=embed)
            return

        if fakemon_name.capitalize() in self.bot.all_starters_list:
            fakemon_id = await add_fakemon_to_database(database=self.bot.db, owner_id=ctx.author.id, fakemon_name=fakemon_name, starter=True)

            await add_fakemon_to_inventory(database=self.bot.db, owner_id=ctx.author.id, fakemon_id=fakemon_id)

            embed = discord.Embed(
                title=f"You have received your {fakemon_name.capitalize()}!", colour=0xDC143C)
            await ctx.send(embed=embed)

            await self.bot.db.execute("UPDATE userinformation SET starter = $1 WHERE userid = $2", True, ctx.author.id)

        else:
            embed = discord.Embed(
                title=f"This fakemon does not exist or is not available as a starter!", colour=0xDC143C)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Starters(bot))
