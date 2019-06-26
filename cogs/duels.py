import discord
from discord.ext import commands
import asyncio
import random
from cogs.database import *
from cogs.fakemon import *
import aiohttp
from functools import partial
from io import BytesIO
from typing import Union
import json
from PIL import Image, ImageDraw, ImageFont


class Duels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=bot.loop)

        with open("pokedex.json", "r", encoding="UTF8") as file:
            pokedex = json.load(file)

    async def get_sprite(self, url: str) -> bytes:
        async with self.session.get(url) as response:
            sprite_bytes = await response.read()

        return sprite_bytes

    @staticmethod
    def processing(user_name, user_level, user_hp, user_max_hp, user_sprite, enemy_name, enemy_level, enemy_hp, enemy_max_hp, enemy_sprite) -> BytesIO:
        with Image.open("cogs/battlescene.png") as bs:

            if user_hp >= 100:
                user_hp_label = "100"
            elif user_hp >= 10:
                user_hp_label = f"0{user_hp}"
            elif user_hp > 0:
                user_hp_label = f"00{user_hp}"
            else:
                user_hp_label = "000"

            if enemy_hp >= 100:
                enemy_hp_label = "100"
            elif enemy_hp >= 10:
                enemy_hp_label = f"0{enemy_hp}"
            elif enemy_hp > 0:
                enemy_hp_label = f"00{enemy_hp}"
            else:
                enemy_hp_label = "000"

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

            draw = ImageDraw.Draw(bs)
            font = ImageFont.truetype('cogs/battlefont.ttf', 25)

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

        final_buffer.seek(0)
        return final_buffer

    @commands.command()
    async def duel(self, ctx, enemy: discord.User):
        # TODO: Add it so both people have to accept.
        # TODO: Check if the server has set a channel.

        # PREPARATIONS
        db = await get_battle_information(database=self.bot.db, user=ctx.author.id, enemy=enemy.id)

        user_sprite = await self.get_sprite(db["User"]["Sprite"])
        enemy_sprite = await self.get_sprite(db["Enemy"]["Sprite"])

        # Start battle
        user_turn = random.choice(["User", "Enemy"])

        # Displays the image once to get the placeholder.
        fn = partial(self.processing, db["User"]
                     ["Name"], db["User"]["Level"], db["User"]["HP"], db["User"]["Max HP"], user_sprite,
                     db["Enemy"]["Name"], db["Enemy"]["Level"], db["Enemy"]["HP"], db["Enemy"]["Max HP"], enemy_sprite)

        final_buffer = await self.bot.loop.run_in_executor(None, fn)
        file = discord.File(filename="bs.png", fp=final_buffer)
        battle_image = await ctx.send(file=file)

        # Displays the message to get the place holder.
        embed = discord.Embed(
            title=f"{ctx.author.name} VS. {enemy.name}", colour=0xDC143C)
        text = await ctx.send(embed=embed)

        while db["User"]["HP"] > 0 or db["Enemy"]["HP"] > 0:
            await asyncio.sleep(2)
            # Switches the turns for the users.
            if user_turn == "User":
                user_turn = "Enemy"
                enemy_user = "User"
            else:
                user_turn = "User"
                enemy_user = "Enemy"

            current_user = ctx.author if user_turn == "User" else enemy

            timeout = False

            # Displays the image for the battle.
            fn = partial(self.processing, db["User"]
                         ["Name"], db["User"]["Level"], db["User"]["HP"], db["User"]["Max HP"], user_sprite,
                         db["Enemy"]["Name"], db["Enemy"]["Level"], db["Enemy"]["HP"], db["Enemy"]["Max HP"], enemy_sprite)

            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="bs.png", fp=final_buffer)
            await battle_image.delete()
            battle_image = await ctx.send(file=file)

            while True:
                if db[user_turn]["Moves"] == [] or timeout:
                    embed = discord.Embed(
                        title=f'{db[user_turn]["Name"]} has no moves!\n{db[user_turn]["Name"]} has used Tackle!', colour=0xDC143C)
                    await text.delete()
                    text = await ctx.send(embed=embed)

                    db[enemy_user]["HP"] -= 10
                    break
                else:
                    moves = {}
                    moves_text = ""

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
                    await ctx.send(embed=embed)

                    # Waits for the move.
                    def check(m):
                        return m.content.capitalize() in moves.keys() and m.author.id == current_user.id

                    try:
                        message = await self.bot.wait_for('message', check=check)
                        move_used = message.content

                        if random.randint(0, moves[move_used["Accuracy"]]) <= moves[move_used["Accuracy"]]:
                            hit = True

                            damage = (
                                ((((2 * db[user_turn]["Level"]) / 5) + 2) * moves[move_used]["Power"]) / 50) + 2

                            db[enemy_user]["HP"] -= damage

                        else:
                            hit = False

                        embed = discord.Embed(
                            title=f'{db["User"]["Name"]} has used {move_used}!\n{"It hit the opponent for " + damage + " damage." if hit == True else "It missed!"}', colour=0xDC143C)
                        await ctx.send(embed=embed)

                        break
                    except asyncio.TimeoutError:
                        timeout = True

        print("BONGO")
        # TODO: Add victory shit


def setup(bot):
    bot.add_cog(Duels(bot))
