import discord
from discord.ext import commands
import asyncio
import typing
from cogs.fakemon import get_random_fakemon, get_fakemon


class Pokedex(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pokedex(self, ctx, fakemon_name: typing.Optional[str]):
        if fakemon_name is None:
            fakemon = await get_random_fakemon(database=self.bot.db)
        else:
            fakemon = await get_fakemon(database=self.bot.db, fakemon=fakemon_name)

        if fakemon is not None:
            if fakemon_name is None:
                embed = discord.Embed(
                    title=f"Pokedex (Random Search Mode)\n{fakemon['name']} | ID: {fakemon['pokedexid']}", colour=0xDC143C)
            else:
                embed = discord.Embed(
                    title=f"Pokedex: {fakemon['name']} | ID: {fakemon['pokedexid']}", colour=0xDC143C)

            embed.set_thumbnail(url=fakemon["imageurl"])
            embed.add_field(name="Type:", value=fakemon["type"], inline=True)

            if fakemon["previousevolution"] == "None" and fakemon["nextevolution"] != "None":
                evolutions = f"{fakemon['name']}'s next evolution is {fakemon['nextevolution']} at level {fakemon['nextevolutionlevel']}!"
            elif fakemon["previousevolution"] == "None" and fakemon["nextevolution"] == "None":
                evolutions = f"{fakemon['name']} has no other evolutions."
            elif fakemon["previousevolution"] != "None" and fakemon["nextevolution"] == "None":
                evolutions = f"{fakemon['name']}'s previous evolution was {fakemon['previousevolution']}!"
            else:
                evolutions = f"{fakemon['name']}'s previous evolution was {fakemon['previousevolution']} and its next evolution is {fakemon['nextevolution']} at level {fakemon['nextevolutionlevel']}"

            embed.add_field(name="Evolutions:", value=evolutions, inline=True)
            embed.add_field(name="Pokedex Entry:",
                            value=fakemon["pokedexentry"], inline=True)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(colour=0xDC143C)
            embed.add_field(
                name=f"Pokedex (Invalid Input)", value="This fakemon does not exist!", inline=True)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Pokedex(bot))
