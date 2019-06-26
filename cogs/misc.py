import discord
from discord.ext import commands
from cogs.database import *


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def money(self, ctx):
        """Displays the current user's money.

        Arguments:
            ctx {var} -- The context of the message.
        """
        user = await get_user_information(database=self.bot.db, user_id=ctx.author.id)

        embed = discord.Embed(
            title=f"Your balance is ₱{user['money']}.", colour=0xDC143C)
        embed.set_footer(text=f"{ctx.author.name}'s bank account.")
        await ctx.send(embed=embed)

    @commands.command()
    async def pay(self, ctx, payee: discord.User, amount: int):
        """Used to pay another player a certain amount of money.

        Arguments:
            ctx {var} -- The context of the message.
            payee {discord.User} -- The user who is going to receive the money.
            amount {int} -- The amount of money given.
        """
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
    async def equip(self, ctx, fakemon_id: int):
        """Equips a pokemon as your main one.

        Arguments:
            ctx {var} -- The context of the message.
            fakemon_id {int} -- The ID of the Fakemon you want to have.
        """
        user_information = await get_user_information(database=self.bot.db, user_id=ctx.author.id)
        fakemon_inventory = user_information["fakemoninventory"]
        current_primary = user_information["primaryfakemon"]

        if fakemon_id not in fakemon_inventory:
            embed = discord.Embed(
                title=f"You don't have this Fakemon!", colour=0xDC143C)
            await ctx.send(embed=embed)
            return

        if current_primary != 0:
            await add_fakemon_to_inventory(database=self.bot.db, owner_id=ctx.author.id, fakemon_id=current_primary)

        await remove_fakemon_from_inventory(database=self.bot.db, owner_id=ctx.author.id, fakemon_id=fakemon_id)

        await self.bot.db.execute('UPDATE userinformation SET primaryfakemon = $1 WHERE userid = $2', fakemon_id, ctx.author.id)

        embed = discord.Embed(
            title=f"You have equipped ID {fakemon_id} as your primary!", colour=0xDC143C)
        await ctx.send(embed=embed)

    @commands.command()
    async def stats(self, ctx, fakemon_id: int):
        """Shows the statistics of any owned Fakemon.

        Arguments:
            ctx {var} -- The context of the message.
            fakemon_id {int} -- The ID of the fakemon.
        """
        fakemon_stats = await get_fakemon_information(database=self.bot.db, fakemon_id=fakemon_id)
        fakemon_information = await self.bot.db.fetchrow('SELECT * FROM allfakemon WHERE name = $1', fakemon_stats["name"])

        inventory_message_list = []

        embed = discord.Embed(colour=0xDC143C)

        for item_id in fakemon_stats["moves"]:
            item = await self.bot.db.fetchrow('SELECT * FROM moves WHERE moveid = $1', item_id)
            inventory_message_list.append(
                f"**{item['movename']}** (ID: {item['moveid']}) | **Power**: {item['movepower']} | **Accuracy**: {item['moveaccuracy']}")

        inventory_message = "\n".join(inventory_message_list)
        embed.set_thumbnail(url=fakemon_information["imageurl"])
        embed.add_field(name="Pokedex Information",
                        value=f'**Name**: {fakemon_stats["name"]}\n**Type**: {fakemon_information["type"]}\n**Level**: {fakemon_stats["level"]}\n**Moves**:\n {inventory_message}\n**IV**: {fakemon_stats["iv"]}')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Misc(bot))
