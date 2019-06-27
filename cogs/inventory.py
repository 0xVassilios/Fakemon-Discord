from cogs.database import get_user_information, get_fakemon_information
from cogs.fakemon import calculate_exp_needed
from discord.ext import commands
import discord


class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def inventory(self, ctx):
        """The base command for the inventory command.

        Arguments:
            ctx {var} -- The context of the message.
        """
        embed = discord.Embed(colour=0xDC143C)
        embed.add_field(name="Inventory System",
                        value="In order to use your inventory write \"f!inventory (fakemon/items/moves) (page number)\".")
        await ctx.send(embed=embed)

    @inventory.command()
    async def fakemon(self, ctx, page: int = 1):
        """Displays all your current fakemon into pages.

        Arguments:
            ctx {var} -- The context of the message.

        Keyword Arguments:
            page {int} -- The page number. (default: {1})
        """
        user = await get_user_information(database=self.bot.db, user_id=ctx.author.id)

        inventory = user["fakemoninventory"]

        # We check if the user has any Fakemon at all.
        if inventory == [] and user["primaryfakemon"] == 0:
            embed = discord.Embed(
                title="You have no fakemon!", colour=0xDC143C)
            await ctx.send(embed=embed)
            return

        # Calculate the total pages with 9 entries per page.
        total_pages = int(len(inventory) / 9) + 1

        # Check if the user has specified an available page.
        if int(page) > int(total_pages):
            embed = discord.Embed(
                title="You don't have this many pages!", colour=0xDC143C)
            await ctx.send(embed=embed)
            return

        first_page = (int(page) * 9) - 10

        if first_page < 0:
            first_page = 0
        second_page = (int(page) * 9)

        inventory_length = len(inventory)
        inventory = inventory[first_page:second_page]
        inventory_message_list = []

        embed = discord.Embed(colour=0xDC143C)

        primary_fakemon_id = user["primaryfakemon"]

        # If the primary fakemon isn't 0 (meaning it doesn't exist) then we display it.
        if primary_fakemon_id != 0:
            fakemon = await get_fakemon_information(database=self.bot.db, fakemon_id=primary_fakemon_id)

            row = await self.bot.db.fetchrow('SELECT * FROM allfakemon WHERE name = $1', fakemon["name"])

            fakemon_type = row["type"]

            xp_for_levelup = await calculate_exp_needed(level=fakemon['level'])

            inventory_message_list.append(
                f"**{fakemon['name']}** (ID: {fakemon['fakemonid']} | Primary)| **Level**: {fakemon['level']} | **Type**: {fakemon_type} | **EXP**: {fakemon['xp']}/{xp_for_levelup} | **IV**: {fakemon['iv']}")

        for fakemon_id in inventory:
            fakemon = await get_fakemon_information(database=self.bot.db, fakemon_id=fakemon_id)

            row = await self.bot.db.fetchrow('SELECT * FROM allfakemon WHERE name = $1', fakemon["name"])

            fakemon_type = row["type"]

            xp_for_levelup = await calculate_exp_needed(level=fakemon['level'])
            inventory_message_list.append(
                f"**{fakemon['name']}**  (ID: {fakemon['fakemonid']})| **Level**: {fakemon['level']} | **Type**: {fakemon_type} | **EXP**: {fakemon['xp']}/{xp_for_levelup} | **IV**: {fakemon['iv']}")

        inventory_message = "\n".join(inventory_message_list)

        embed.add_field(
            name=f"Your Fakemon Inventory:", value=inventory_message)
        embed.set_footer(
            text=f"{page} out of {int(total_pages)} pages. You have {inventory_length + 1} Fakemon.")
        await ctx.send(embed=embed)

    @inventory.command()
    async def items(self, ctx, page: int = 1):
        """Displays the items.

        Arguments:
            ctx {var} -- The context of the page.

        Keyword Arguments:
            page {int} -- The number of th page to display. (default: {1})
        """
        user = await get_user_information(database=self.bot.db, user_id=ctx.author.id)
        inventory = user["iteminventory"]
        # Checks if he has anything.
        if inventory == []:
            embed = discord.Embed(
                title="You have no items!", colour=0xDC143C)
            await ctx.send(embed=embed)
            return

        total_pages = int(len(inventory) / 10) + 1

        if int(page) > int(total_pages):
            embed = discord.Embed(
                title="You don't have this many pages!", colour=0xDC143C)
            await ctx.send(embed=embed)
            return

        first_page = (int(page) * 10) - 11

        if first_page < 0:
            first_page = 0
        second_page = (int(page) * 10)

        inventory_length = len(inventory)
        inventory = inventory[first_page:second_page]
        inventory_message_list = []

        embed = discord.Embed(colour=0xDC143C)

        item_list = await self.bot.db.fetchrow('SELECT * FROM userinformation WHERE userid = $1', ctx.author.id)

        for item_id in item_list["iteminventory"]:
            item = await self.bot.db.fetchrow('SELECT * FROM items WHERE itemid = $1', item_id)
            inventory_message_list.append(
                f"**{item['itemname']}** | {item['itemdescription']}")

        inventory_message = "\n".join(inventory_message_list)

        embed.add_field(
            name=f"Your Item Inventory:", value=inventory_message)
        embed.set_footer(
            text=f"{page} out of {int(total_pages)} pages. You have {inventory_length} items.")
        await ctx.send(embed=embed)

    @inventory.command()
    async def moves(self, ctx, page: int = 1):
        """Displays all available moves.

        Arguments:
            ctx {var} -- The context of the message.

        Keyword Arguments:
            page {int} -- The number of the page to display. (default: {1})
        """
        user = await get_user_information(database=self.bot.db, user_id=ctx.author.id)

        inventory = user["moveinventory"]
        # Checks if he has anything.
        if inventory == []:
            embed = discord.Embed(
                title="You have no moves!", colour=0xDC143C)
            await ctx.send(embed=embed)
            return

        total_pages = int(len(inventory) / 10) + 1

        if int(page) > int(total_pages):
            embed = discord.Embed(
                title="You don't have this many pages!", colour=0xDC143C)
            await ctx.send(embed=embed)
            return

        first_page = (int(page) * 10) - 11

        if first_page < 0:
            first_page = 0
        second_page = (int(page) * 10)

        inventory_length = len(inventory)
        inventory = inventory[first_page:second_page]
        inventory_message_list = []

        embed = discord.Embed(colour=0xDC143C)

        move_list = await self.bot.db.fetchrow('SELECT * FROM userinformation WHERE userid = $1', ctx.author.id)

        for item_id in move_list["moveinventory"]:
            item = await self.bot.db.fetchrow('SELECT * FROM moves WHERE moveid = $1', item_id)
            inventory_message_list.append(
                f"**{item['movename']}** (ID: {item['moveid']})| **Type**: {item['movetype']} | **Power**: {item['movepower']} | **Accuracy**: {item['moveaccuracy']}")

        inventory_message = "\n".join(inventory_message_list)

        embed.add_field(
            name=f"Your Move Inventory:", value=inventory_message)
        embed.set_footer(
            text=f"{page} out of {int(total_pages)} pages. You have {inventory_length} moves.")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Inventory(bot))
