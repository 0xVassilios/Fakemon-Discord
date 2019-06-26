import discord
from discord.ext import commands
from cogs.database import *


class LearnMoves(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def teach(self, ctx, fakemon_id: int, move_id: int):
        """Teaches a move to a Fakemon.

        Arguments:
            ctx {var} -- The context of the message.
            fakemon_id {int} -- The ID of the fakemon that needs to learn the move.
            move_id {int} -- The ID of the move which you are going to teach.
        """
        fakemon_information = await get_fakemon_information(database=self.bot.db, fakemon_id=fakemon_id)

        user_information = await get_user_information(database=self.bot.db, user_id=ctx.author.id)

        move_row = await self.bot.db.fetchrow('SELECT * FROM moves WHERE moveid = $1', move_id)

        fakemon_row = await self.bot.db.fetchrow('SELECT * FROM allfakemon WHERE name = $1', fakemon_information["name"])

        if fakemon_information is None:
            embed = discord.Embed(
                title="You don't have this fakemon!", colour=0xDC143C)
            await ctx.send(embed=embed)
            return

        if move_row is None:
            embed = discord.Embed(
                title="You don't have this move!", colour=0xDC143C)
            await ctx.send(embed=embed)
            return

        move_type = move_row["movetype"]

        if move_type.capitalize() not in fakemon_row["type"]:
            embed = discord.Embed(
                title=f"Your {fakemon_information['name']} cannot learn a {move_type} move!", colour=0xDC143C)
            await ctx.send(embed=embed)
            return

        current_fakemon_moves = fakemon_information["moves"]
        current_fakemon_moves.append(move_id)

        await self.bot.db.execute('UPDATE ownedfakemon SET moves = $1 WHERE fakemonid = $2', current_fakemon_moves, fakemon_id)

        current_user_moves = user_information["moveinventory"]
        current_user_moves.remove(move_id)

        await self.bot.db.execute('UPDATE userinformation SET moveinventory = $1 WHERE userid = $2', current_user_moves, ctx.author.id)

        embed = discord.Embed(
            title=f"Your {fakemon_information['name']} has learned {move_row['movename']}!", colour=0xDC143C)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(LearnMoves(bot))
