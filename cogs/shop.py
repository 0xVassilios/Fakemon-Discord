import discord
from discord.ext import commands
import asyncio
import random
from cogs.database import get_user_information


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(self.change_shop_items())

    async def change_shop_items(self):
        while True:
            # Delete all content from shop.
            await self.bot.db.execute('TRUNCATE shop; DELETE FROM shop;')

            # Choose 5 random moves.
            rows = await self.bot.db.fetch("SELECT * FROM moves ORDER BY random() LIMIT 5;""")

            for row in rows:
                await self.bot.db.execute('INSERT INTO shop VALUES($1, $2, $3, $4)', random.randint(100000, 999999), row["movename"], f'Type: {row["movetype"]} | Power: {row["movepower"]} | Accuracy: {row["moveaccuracy"]}', random.randint(1, 1001))

            row = await self.bot.db.fetchrow("SELECT * FROM items ORDER BY random() LIMIT 1;""")
            await self.bot.db.execute('INSERT INTO shop VALUES($1, $2, $3, $4)', random.randint(100000, 999999), row["itemname"], row["itemdescription"], random.randint(1000, 2001))

            await asyncio.sleep(60 * 30)

    @commands.group(invoke_without_command=True)
    async def shop(self, ctx):
        shop_items = await self.bot.db.fetch('SELECT * FROM shop')
        embed = discord.Embed(colour=0xDC143C)
        shop_text = ""

        for item in shop_items:
            shop_text += f'ID: {item["itemid"]} | **{item["itemname"]}** | Description: {item["itemdescription"]} | Price: {item["itemprice"]}\n\n'

        embed.add_field(name="Joe's Shop & Trade", value=shop_text)
        embed.set_footer(text='Use "f!shop buy (itemid)" to buy an item!')
        await ctx.send(embed=embed)

    @shop.command()
    async def buy(self, ctx, *, item_id: int):
        item = await self.bot.db.fetchrow('SELECT * FROM shop WHERE itemid = $1', item_id)

        user = await get_user_information(database=self.bot.db, user_id=ctx.author.id)

        if item is None:
            embed = discord.Embed(
                title="This item doesn't exist", colour=0xDC143C)
            await ctx.send(embed=embed)
            return

        if user["money"] < item["itemprice"]:
            embed = discord.Embed(
                title="You do not have enough money to buy this item!", colour=0xDC143C)
            await ctx.send(embed=embed)
            return

        current_money = user["money"] - item["itemprice"]

        if item["itemname"] in ["Discount Coupon", "Master Ball", "Rare Candy", "Egg"]:

            item_id = await self.bot.db.fetchrow(
                'SELECT itemid FROM items WHERE itemname = $1', item["itemname"])

            inventory = user["iteminventory"]
            inventory.append(int(item_id["itemid"]))

            await self.bot.db.fetch(
                'UPDATE userinformation SET iteminventory = $1 WHERE userid = $2', inventory, ctx.author.id)

            embed = discord.Embed(
                title=f"You have bought an {item['itemname']}!", colour=0xDC143C)
            await ctx.send(embed=embed)

        else:
            move_id = await self.bot.db.fetchrow(
                'SELECT moveid FROM moves WHERE movename = $1', item["itemname"])

            inventory = user["moveinventory"]
            inventory.append(int(move_id["moveid"]))

            await self.bot.db.fetch(
                'UPDATE userinformation SET moveinventory = $1 WHERE userid = $2', inventory, ctx.author.id)

            embed = discord.Embed(
                title=f"You have bought the move {item['itemname']}!", colour=0xDC143C)
            await ctx.send(embed=embed)

        await self.bot.db.execute('UPDATE userinformation SET money = $1 WHERE userid = $2', current_money, ctx.author.id)


def setup(bot):
    bot.add_cog(Shop(bot))
