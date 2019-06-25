import discord
from discord.ext import commands
from cogs.database import *


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def money(self, ctx):
        user = await get_user_information(database=self.bot.db, user_id=ctx.author.id)

        embed = discord.Embed(
            title=f"Your balance is ₱{user['money']}.", colour=0xDC143C)
        embed.set_footer(text=f"{ctx.author.name}'s bank account.")
        await ctx.send(embed=embed)

    @commands.command()
    async def pay(self, ctx, payee: discord.User, amount: int):
        user = await get_user_information(database=self.bot.db, user_id=ctx.author.id)

        if user["money"] > amount:
            embed = discord.Embed(
                title=f"You don't have enough ₱ to send.", colour=0xDC143C)
            embed.set_footer(text=f"{ctx.author.name}'s bank account.")
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Misc(bot))
