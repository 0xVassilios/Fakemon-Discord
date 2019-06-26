from cogs.database import *
from cogs.fakemon import *
from discord.ext import commands
from functools import partial
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from typing import Union
import aiohttp
import asyncio
import discord
import json
import random


class Duels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=bot.loop)

        # We load the JSON since it's faster for searching than querying the database.
        with open("pokedex.json", "r", encoding="UTF8") as file:
            pokedex = json.load(file)

    async def get_sprite(self, url: str) -> bytes:
        """We get the URL of the Fakemon through the JSON then retrieve its bytes.

        Arguments:
            url {str} -- The url of the sprite.

        Returns:
            bytes -- The bytes of the sprite.
        """
        async with self.session.get(url) as response:
            sprite_bytes = await response.read()

        return sprite_bytes

    @staticmethod
    def processing(user_name, user_level, user_hp, user_max_hp, user_sprite, enemy_name, enemy_level, enemy_hp, enemy_max_hp, enemy_sprite) -> BytesIO:
        """This function processes the image (battlescene.png) and turns it into bytes to be sent on Discord.

        Arguments:
            user_name {str} -- The name of the first person's Fakemon.
            user_level {int} -- The level of the first person's Fakemon.
            user_hp {int} -- The current health points of the first person's Fakemon.
            user_max_hp {int} -- The maximum possible health points of the first person's Fakemon.
            user_sprite {bytes} -- The sprite of the first person's Fakemon.

            enemy_name {str} -- The name of the second person's Fakemon.
            enemy_level {int} -- The level of the second person's Fakemon.
            enemy_hp {int} -- The current health points of the second person's Fakemon.
            enemy_max_hp {int} -- The maximum possible health points of the second person's Fakemon.
            enemy_sprite {bytes} -- The sprite of the second person's Fakemon.

        Returns:
            BytesIO -- The image made turned into bytes.
        """
        with Image.open("cogs/battlescene.png") as bs:

            # We get the percentage of the current Fakemon's health in order to get the right health points bar.
            user_hp_label = int(((100 * user_hp) / user_max_hp))
            enemy_hp_label = int(((100 * enemy_hp) / enemy_max_hp))

            # Since we use ""weird"" names for our files due to GitHub sorting, we make it so we get the right files.
            if user_hp_label >= 100:
                user_hp_label = "100"
            elif user_hp_label >= 10:
                user_hp_label = f"0{user_hp_label}"
            elif user_hp_label > 0:
                user_hp_label = f"00{user_hp_label}"
            else:
                user_hp_label = "000"

            if enemy_hp_label >= 100:
                enemy_hp_label = "100"
            elif enemy_hp_label >= 10:
                enemy_hp_label = f"0{enemy_hp_label}"
            elif enemy_hp_label > 0:
                enemy_hp_label = f"00{enemy_hp_label}"
            else:
                enemy_hp_label = "000"

            # Opening the health bars and sprites then pasting them on the correct coordinates.
            with Image.open(f"hp_bars/{user_hp_label}.png") as hp:
                bs.paste(hp, (315, 171), mask=hp)

            with Image.open(f"hp_bars/{enemy_hp_label}.png") as hp:
                bs.paste(hp, (31, 39), mask=hp)

            with Image.open(BytesIO(user_sprite)) as sprite:
                sprite.thumbnail((150, 150))
                bs.paste(sprite, (74, 105), mask=sprite)

            with Image.open(BytesIO(enemy_sprite)) as sprite:
                sprite.thumbnail((150, 150))
                bs.paste(sprite, (343, 8), mask=sprite)

            # Settings up the variable and settings for our font.
            draw = ImageDraw.Draw(bs)
            font = ImageFont.truetype('cogs/battlefont.ttf', 25)

            # These lines write all the kind of texts in the format draw.text((coordinates), text, (RGB colour), font)
            draw.text((323, 176), user_name, (0, 0, 0), font=font)
            draw.text((41, 44), enemy_name, (0, 0, 0), font=font)

            draw.text((442, 182), f"Level  {user_level}", (0, 0, 0), font=font)
            draw.text(
                (158, 49), f"Level  {enemy_level}", (0, 0, 0), font=font)

            draw.text(
                (415, 220), f"HP: {user_hp}/{user_max_hp}", (0, 0, 0), font=font)
            draw.text(
                (132, 87), f"HP: {enemy_hp}/{enemy_max_hp}", (0, 0, 0), font=font)

            final_buffer = BytesIO()
            bs.save(final_buffer, "png")

        # We return to the first byte as in not to give an error and return it.
        final_buffer.seek(0)
        return final_buffer

    @commands.command()
    async def duel(self, ctx, enemy: discord.User):
        """This command is used to start a duel with another user.

        Arguments:
            ctx {var} -- The context of the message sent.
            enemy {discord.User} -- The enemy for your duel.
        """
        user = await get_user_information(database=self.bot.db, user_id=ctx.author.id)
        enemy_info = await get_user_information(database=self.bot.db, user_id=enemy.id)

        """
        We firstly check if the user has a primary Fakemon set. If not then the default value is 0.
        If he doesn't have a primary fakemon then it says so and stops the function.
        """
        if user["primaryfakemon"] == 0 or enemy_info["primaryfakemon"] == 0:
            embed = discord.Embed(
                title=f'{ctx.author.name if user["primaryfakemon"] == 0 else enemy.name} doesn\'t have a Fakemon equipped!', colour=0xDC143C)
            embed.set_footer(text="Use `f!equip (Fakemon ID)`")
            await ctx.send(embed=embed)
            return

        """
        The same way like primary Fakemon, if an administrator of a guild hasn't set the category where battles should happen then ...
        ... it says so and it returns nothing in order to cancel it.
        """
        guild_info = await self.bot.db.fetchrow('SELECT * FROM channels WHERE server = $1', ctx.guild.id)

        if guild_info["battles"] == "0":
            embed = discord.Embed(
                title=f'This guild doesn\'t have a battle category!', colour=0xDC143C)
            embed.set_footer(
                text="An admin has to execute `f!set location battles (category name)`")
            await ctx.send(embed=embed)
            return

        """
        If all the checks have been passed then we move onto the next check. This is to check if both users want to duel.
        A message is sent with an emoji. If both users click it then a duel ensues.
        """
        embed = discord.Embed(
            title=f"Battle Request: {ctx.author.name} <=> {enemy.name}", colour=0xDC143C)

        battle_request = await ctx.send(embed=embed)
        await battle_request.add_reaction("✅")

        users_battling = [ctx.author.id, enemy.id]

        def check(reaction, user):
            return user.id in users_battling and str(reaction.emoji) == "✅"

        # We do this twice so we can make sure that both people have liked it.
        try:
            for i in range(2):
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                users_battling.remove(user.id)
        except asyncio.TimeoutError:
            await battle_request.clear_reactions()
            embed = discord.Embed(
                title=f"The battle request has timed out.", colour=0xDC143C)
            await battle_request.edit(embed=embed)
            return

        await battle_request.clear_reactions()

        embed = discord.Embed(
            title=f"A channel called `battles-{ctx.author.name}-vs-{enemy.name}` has been created.", colour=0xDC143C)
        await battle_request.edit(embed=embed)

        """
        These are the settings for the new channel that is going to be made for the battle. Only the two duellers (?) are able to speak in that channel.
        """
        guild = ctx.message.guild

        overwrites = {
            ctx.message.author: discord.PermissionOverwrite(send_messages=True),
            enemy: discord.PermissionOverwrite(send_messages=True),
            guild.default_role: discord.PermissionOverwrite(
                send_messages=False)
        }

        channel = discord.utils.get(
            guild.categories, id=guild_info["battles"])

        battle_channel = await guild.create_text_channel(f'battles-{ctx.author.name}-vs-{enemy.name}', overwrites=overwrites, category=channel)

        # We prepare all variables by getting the sprites and a dictionary of all relevant information.
        db = await get_battle_information(database=self.bot.db, user=ctx.author.id, enemy=enemy.id)

        user_sprite = await self.get_sprite(db["User"]["Sprite"])
        enemy_sprite = await self.get_sprite(db["Enemy"]["Sprite"])

        # This random choice is to choose who is going to start first.
        user_turn = random.choice(["User", "Enemy"])

        # By using partial we can make the battle image without disrupting the current flow of the program.
        fn = partial(self.processing, db["User"]
                     ["Name"], db["User"]["Level"], db["User"]["HP"], db["User"]["Max HP"], user_sprite,
                     db["Enemy"]["Name"], db["Enemy"]["Level"], db["Enemy"]["HP"], db["Enemy"]["Max HP"], enemy_sprite)

        final_buffer = await self.bot.loop.run_in_executor(None, fn)
        file = discord.File(filename="bs.png", fp=final_buffer)
        battle_image = await battle_channel.send(file=file)

        # This is the first message that is sent which shows the two contestants and also we get a placeholder for future text.
        embed = discord.Embed(
            title=f"{ctx.author.name} VS. {enemy.name}", colour=0xDC143C)
        await battle_channel.send(embed=embed)

        """
        For some reason our first while loop was having bugs and all but this one seems to be working so there it is.
        It is a few lines more but it works 100% of the times now. Also if you are reading this I respect you.
        """
        while True:
            if db["User"]["HP"] <= 0:
                break

            if db["Enemy"]["HP"] <= 0:
                break

            await asyncio.sleep(2)

            # This way we can switch who is the current user that is playing.
            if user_turn == "User":
                user_turn = "Enemy"
                enemy_user = "User"
            else:
                user_turn = "User"
                enemy_user = "Enemy"

            current_user = ctx.author if user_turn == "User" else enemy

            timeout = False

            # By using the afforementioned command (partial) we get the newer image.
            fn = partial(self.processing, db["User"]
                         ["Name"], db["User"]["Level"], db["User"]["HP"], db["User"]["Max HP"], user_sprite,
                         db["Enemy"]["Name"], db["Enemy"]["Level"], db["Enemy"]["HP"], db["Enemy"]["Max HP"], enemy_sprite)

            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="bs.png", fp=final_buffer)

            # Delete both text and image as we can't really edit them due to Discord limitations.
            await text.delete()
            await battle_image.delete()
            battle_image = await battle_channel.send(file=file)

            """
            We contain everything in another while True loop because if the user doesn't have time to reply to the question about which
            move to make then it does the default Tackle and breaks.
            """
            while True:
                # If user has no moves or is in a timeout then we do a default tackle.
                if db[user_turn]["Moves"] == [] or timeout:
                    embed = discord.Embed(
                        title=f'{db[user_turn]["Name"]} has no moves!\n{db[user_turn]["Name"]} has used Tackle!', colour=0xDC143C)
                    text = await battle_channel.send(embed=embed)

                    db[enemy_user]["HP"] -= 10
                    break

                # Otherwise we continue with their moves.
                else:
                    # We get a dictionary for all the move statistics then a string for what will be showing for easier access.
                    moves = {}
                    moves_text = ""

                    # For every move in the dictionary that was made, we query the database for the statistics then add it to our string and dictionary.
                    for move in db[user_turn]["Moves"]:
                        move_info = await self.bot.db.fetchrow('SELECT * FROM moves WHERE moveid = $1', move)

                        moves_text += f'**{move_info["movename"]}** | **Power**: {move_info["movepower"]} | **Accuracy**: {move_info["moveaccuracy"]}\n'

                        moves[move_info["movename"]] = {
                            "Power": move_info["movepower"],
                            "Accuracy": move_info["moveaccuracy"]
                        }

                    embed = discord.Embed(
                        title=f'It\'s {current_user.name}\'s turn!', colour=0xDC143C)
                    embed.add_field(name="Choose your move!", value=moves_text)
                    embed.set_footer(text="TIP: Just type the name!")
                    moves_text = await battle_channel.send(embed=embed)

                    # We use this check to see if the move is valid from the dictionary and also if the correct person responds.
                    def check(m):
                        return m.content.capitalize() in moves.keys() and m.author.id == current_user.id

                    try:
                        message = await self.bot.wait_for('message', check=check)
                        move_used = message.content.capitalize()
                        await message.delete()

                        # We check if the move is successful by checking if our random roll is less or equal than it.
                        if random.randint(0, int(moves[move_used]["Accuracy"])) <= int(moves[move_used]["Accuracy"]):
                            hit = True

                            # This is the default Pokemon damage roll which we are using a modified version for Fakemon.
                            damage = int((
                                ((((2 * db[user_turn]["Level"]) / 5) + 2) * moves[move_used]["Power"]) / 50) + 2)

                            db[enemy_user]["HP"] -= damage

                        # If our roll is unsuccessful we didn't hit.
                        else:
                            hit = False

                        # If hit = True then it shows the damage and the move otherwise it's a miss.
                        embed = discord.Embed(
                            title=f'{db["User"]["Name"]} has used {move_used}!\n{"It hit the opponent for " + str(damage) + " damage." if hit == True else "It missed!"}', colour=0xDC143C)
                        text = await battle_channel.send(embed=embed)
                        await moves_text.delete()

                        break

                    # If they don't reply in time then they go into timeout.
                    except asyncio.TimeoutError:
                        timeout = True

        # We said about this before.
        fn = partial(self.processing, db["User"]
                     ["Name"], db["User"]["Level"], db["User"]["HP"], db["User"]["Max HP"], user_sprite,
                     db["Enemy"]["Name"], db["Enemy"]["Level"], db["Enemy"]["HP"], db["Enemy"]["Max HP"], enemy_sprite)

        final_buffer = await self.bot.loop.run_in_executor(None, fn)
        file = discord.File(filename="bs.png", fp=final_buffer)

        await text.delete()
        await battle_image.delete()

        battle_image = await battle_channel.send(file=file)

        embed = discord.Embed(
            title=f'{db["Enemy"]["Name"] if db["User"]["HP"] <= 0 else db["User"]["Name"]} has won the battle!', colour=0xDC143C)
        await battle_channel.send(embed=embed)

        # This determines who the winner is.
        if db["User"]["HP"] <= 0:
            winner = "Enemy"
            loser = "User"
        else:
            winner = "User"
            loser = "Enemy"

        """
        Here we calculate the rewards for the battle using once again a modified formula.
        The loser gets half the stuff of the winner.
        """
        exp = int((1.5 * random.randint(10, 201) *
                   db[loser]["Level"] * 1.5) / 1.5 * 7)
        money = int(exp / 2)

        if winner == "User":
            await give_money(database=self.bot.db, user_id=ctx.author.id, amount=money)
            await give_money(database=self.bot.db, user_id=enemy.id, amount=int(money / 2))

            await give_xp_to_fakemon(database=self.bot.db, user_id=ctx.author.id, amount=exp)
            await give_xp_to_fakemon(database=self.bot.db, user_id=enemy.id, amount=int(exp / 2))
        else:
            await give_money(database=self.bot.db, user_id=enemy.id, amount=money)
            await give_money(database=self.bot.db, user_id=ctx.author.id, amount=int(money / 2))

            await give_xp_to_fakemon(database=self.bot.db, user_id=enemy.id, amount=exp)
            await give_xp_to_fakemon(database=self.bot.db, user_id=ctx.author.id, amount=int(exp / 2))

        # Just a mess of an embed that shows the rewards for everyone.
        embed = discord.Embed(colour=0xDC143C)

        rewards = f'''**{db["Enemy"]["Name"] if db["User"]["HP"] <= 0 else db["User"]["Name"]}**:\nEXP: {exp}\nMoney: {money}\n\n
            **{db["Enemy"]["Name"] if db["User"]["HP"] > 0 else db["User"]["Name"]}**\nEXP: {int(exp / 2)}\nMoney: {int(money / 2)}\n\n'''

        embed.add_field(name='Battle Rewards:', value=rewards)
        await battle_channel.send(embed=embed)

        await asyncio.sleep(10)
        await battle_channel.delete()

        user = await get_user_information(database=self.bot.db, user_id=ctx.author.id)
        enemy_info = await get_user_information(database=self.bot.db, user_id=enemy.id)

        await check_levelup(database=self.bot.db, fakemon_id=user["primaryfakemon"])
        await check_levelup(database=self.bot.db, fakemon_id=enemy_info["primaryfakemon"])


def setup(bot):
    bot.add_cog(Duels(bot))
