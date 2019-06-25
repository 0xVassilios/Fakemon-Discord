import discord
from discord.ext import commands
from cogs.database import get_user_information, get_fakemon_information
from cogs.fakemon import calculate_exp_needed


class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def inventory(self, ctx):
        embed = discord.Embed(colour=0xDC143C)
        embed.add_field(name="Inventory System",
                        value="In order to use your inventory write \"f!inventory show (fakemon/items/moves) (page number)\".")
        await ctx.send(embed=embed)

    @inventory.command()
    async def show(self, ctx, inventory_type: str, page: int = 1):
        if inventory_type.lower() not in ["fakemon", "moves", "items"]:
            embed = discord.Embed(
                title="You chose an invalid inventory type!", colour=0xDC143C)
            await ctx.send(embed=embed)
            return

        user = await get_user_information(database=self.bot.db, user_id=ctx.author.id)

        if inventory_type.lower() == "fakemon":
            inventory = user["fakemoninventory"]
            # Checks if he has anything.
            if inventory == []:
                embed = discord.Embed(
                    title="You have no fakemon!", colour=0xDC143C)
                await ctx.send(embed=embed)
                return

        elif inventory_type.lower() == "moves":
            inventory = user["moveinventory"]
            # Checks if he has anything.
            if inventory == []:
                embed = discord.Embed(
                    title="You have no moves!", colour=0xDC143C)
                await ctx.send(embed=embed)
                return

        elif inventory_type.lower() == "items":
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

        inventory = inventory[first_page:second_page]
        inventory_message_list = []

        embed = discord.Embed(colour=0xDC143C)

        if inventory_type.lower() == "fakemon":
            primary_fakemon_id = user["primaryfakemon"]

            if primary_fakemon_id != 0:
                fakemon = await get_fakemon_information(database=self.bot.db, fakemon_id=primary_fakemon_id)
                xp_for_levelup = await calculate_exp_needed(level=fakemon['level'])
                inventory_message_list.append(
                    f"**{fakemon['name']}** (ID: {fakemon['fakemonid']} | Primary)| Level: {fakemon['level']} | EXP: {fakemon['xp']}/{xp_for_levelup} | IV: {fakemon['iv']}")

            for fakemon_id in inventory:
                fakemon = await get_fakemon_information(database=self.bot.db, fakemon_id=fakemon_id)
                xp_for_levelup = await calculate_exp_needed(level=fakemon['level'])
                inventory_message_list.append(
                    f"**{fakemon['name']}**  (ID: {fakemon['fakemonid']})| Level: {fakemon['level']} | EXP: {fakemon['xp']}/{xp_for_levelup} | IV: {fakemon['iv']}")

        elif inventory_type.lower() == "items":
            item_list = await self.bot.db.fetchrow('SELECT * FROM userinformation WHERE userid = $1', ctx.author.id)

            for item_id in item_list["iteminventory"]:
                item = await self.bot.db.fetchrow('SELECT * FROM items WHERE itemid = $1', item_id)
                inventory_message_list.append(
                    f"**{item['itemname']}** | {item['itemdescription']}")

        elif inventory_type.lower() == "moves":
            move_list = await self.bot.db.fetchrow('SELECT * FROM userinformation WHERE userid = $1', ctx.author.id)

            for item_id in move_list["moveinventory"]:
                item = await self.bot.db.fetchrow('SELECT * FROM moves WHERE moveid = $1', item_id)
                inventory_message_list.append(
                    f"**{item['movename']}** | **Type**: {item['movetype']} | **Power**: {item['movepower']} | **Accuracy**: {item['moveaccuracy']}")

        inventory_message = "\n".join(inventory_message_list)

        embed.add_field(
            name=f"Your {inventory_type.capitalize()} Inventory:", value=inventory_message)
        embed.set_footer(text=f"{page} out of {int(total_pages)} pages.")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Inventory(bot))
