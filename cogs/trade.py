import discord
from discord.ext import commands
from cogs.database import get_user_information, get_fakemon_information, add_fakemon_to_inventory, remove_fakemon_from_inventory
import asyncio


class Trade(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def trade(self, ctx, your_fakemon_id: int, other_user: discord.User, other_fakemon_id: int):
        user_one_information = await get_user_information(database=self.bot.db, user_id=ctx.author.id)
        fakemon_one_information = await get_fakemon_information(database=self.bot.db, fakemon_id=your_fakemon_id)

        user_two_information = await get_user_information(database=self.bot.db, user_id=other_user.id)
        fakemon_two_information = await get_fakemon_information(database=self.bot.db, fakemon_id=other_fakemon_id)

        if fakemon_one_information is not None:
            fakemon_one_id = fakemon_one_information["fakemonid"]
        else:
            fakemon_one_id = None

        if fakemon_two_information is not None:
            fakemon_two_id = fakemon_two_information["fakemonid"]
        else:
            fakemon_two_id = None

        if fakemon_one_id is None or fakemon_one_id not in user_one_information["fakemoninventory"]:
            embed = discord.Embed(
                title=f"You don't have a Fakemon with the ID {your_fakemon_id}!", colour=0xDC143C)
            await ctx.send(embed=embed)
            return
        elif fakemon_two_id is None or fakemon_two_id not in user_two_information["fakemoninventory"]:
            embed = discord.Embed(
                title=f"The other user doesn't have a Fakemon with the ID {other_fakemon_id}!", colour=0xDC143C)
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"Trade Request: {ctx.author.name} <=> {other_user.name}", colour=0xDC143C)

        for fakemon in [fakemon_one_information, fakemon_two_information]:
            move_list = []

            for move in fakemon["moves"]:
                row = await self.bot.db.fetchrow(
                    'SELECT * FROM moves WHERE moveid = $1', move)
                move_list.append(row["movename"])

            moves = ", ".join(move_list)

            if moves == "":
                moves = "No Moves."

            embed.add_field(
                name=fakemon["name"], value=f'**Level**: {fakemon["level"]}\n**EXP**: {fakemon["xp"]}\n**Moves**: {moves}\n**IV**: {fakemon["iv"]}')

        trade_request = await ctx.send(embed=embed)
        await trade_request.add_reaction("✅")

        users_trading = [ctx.author.id, other_user.id]

        def check(reaction, user):
            return user.id in users_trading and str(reaction.emoji) == "✅"

        try:
            for i in range(2):
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                users_trading.remove(user.id)
        except asyncio.TimeoutError:
            await trade_request.clear_reactions()
            embed = discord.Embed(
                title=f"The trade request has timed out.", colour=0xDC143C)
            await trade_request.edit(embed=embed)
            return

        await trade_request.clear_reactions()
        embed = discord.Embed(
            title=f"Trade has been processed!", colour=0xDC143C)
        embed.set_footer(text=f"{ctx.author.name} <=> {other_user.name}")
        await trade_request.edit(embed=embed)

        await remove_fakemon_from_inventory(database=self.bot.db, owner_id=ctx.author.id, fakemon_id=fakemon_one_id)
        await remove_fakemon_from_inventory(database=self.bot.db, owner_id=other_user.id, fakemon_id=fakemon_two_id)\

        await add_fakemon_to_inventory(database=self.bot.db, owner_id=ctx.author.id, fakemon_id=fakemon_two_id)
        await add_fakemon_to_inventory(database=self.bot.db, owner_id=other_user.id, fakemon_id=fakemon_one_id)


def setup(bot):
    bot.add_cog(Trade(bot))
