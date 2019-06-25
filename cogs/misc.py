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

        payee_information = await get_user_information(database=self.bot.db, user_id=payee.id)

        if user["money"] < amount:
            embed = discord.Embed(
                title=f"You don't have enough ₱ to send.", colour=0xDC143C)
            embed.set_footer(text=f"{ctx.author.name}'s bank account.")
            await ctx.send(embed=embed)
            return

        payee_money = payee_information["money"]
        payee_money += amount

        user_money = user["money"]
        user_money -= amount

        await self.bot.db.execute('UPDATE userinformation SET money = $1 WHERE userid = $2', payee_money, payee.id)
        await self.bot.db.execute('UPDATE userinformation SET money = $1 WHERE userid = $2', user_money, ctx.author.id)

        embed = discord.Embed(
            title=f"You have sent ₱{amount} to {payee.name}.", colour=0xDC143C)
        embed.set_footer(text=f"{ctx.author.name}'s bank account.")
        await ctx.send(embed=embed)

    @commands.command()
    async def givefakemon(self, ctx, user: discord.User, fakemon_id: int):
        pass


def setup(bot):
    bot.add_cog(Misc(bot))
