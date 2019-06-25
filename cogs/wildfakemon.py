import discord
from discord.ext import commands
import asyncio
import random
from cogs.fakemon import get_random_fakemon
from cogs.database import get_random_question, add_fakemon_to_database, add_fakemon_to_inventory


class WildFakemon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(self.generate_fakemon())

    async def generate_fakemon(self):
        while True:
            for guild in self.bot.guilds:
                try:
                    row = await self.bot.db.fetchrow('SELECT * FROM channels WHERE server = $1', guild.id)

                    if row["wilderness"] == 0:
                        return

                    fakemon = await get_random_fakemon(database=self.bot.db)
                    question, answer = await get_random_question(database=self.bot.db)

                    embed = discord.Embed(
                        title=f"A wild {fakemon['name']} appeared!", colour=0xDC143C)
                    embed.set_thumbnail(url=fakemon["imageurl"])
                    embed.add_field(name=f"{question} ({len(answer.split(' '))} words.)",
                                    value=f"Reply with 'f!catch (answer)' in order to capture the {fakemon['name']}!")
                    channel = self.bot.get_channel(row["wilderness"])
                    fakemon_embed = await channel.send(embed=embed)

                    def check(m):
                        m = m.content.split(" ")
                        return m[0] == "f!catch" and " ".join(m[1:]) == answer

                    try:
                        message = await self.bot.wait_for('message', check=check, timeout=60.0)
                        fakemon_id = await add_fakemon_to_database(database=self.bot.db, owner_id=message.author.id, fakemon_name=fakemon["name"], starter=False)
                        await add_fakemon_to_inventory(database=self.bot.db, owner_id=message.author.id, fakemon_id=fakemon_id)

                        embed = discord.Embed(
                            title=f"{message.author.name} has captured the {fakemon['name']}!", colour=0xDC143C)
                        await fakemon_embed.edit(embed=embed)
                    except asyncio.TimeoutError:
                        embed = discord.Embed(
                            title=f"{fakemon['name']} has run away!", colour=0xDC143C)
                        await fakemon_embed.edit(embed=embed)
                except:
                    pass

            await asyncio.sleep(random.randint(60, 60 * 5))


def setup(bot):
    bot.add_cog(WildFakemon(bot))
