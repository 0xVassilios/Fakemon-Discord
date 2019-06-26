from cogs.database import *
from cogs.fakemon import get_random_fakemon, check_levelup
from discord.ext import commands
import discord
import random
import time


class Adventures(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def explore(self, ctx):
        """Base command for the explore action.

        Arguments:
            ctx {var} -- context of the sent message.
        """
        embed = discord.Embed(colour=0xDC143C)
        embed.add_field(name="You are about to embark on your own adventure!",
                        value="Just type 'f!explore start (duration in minutes)' and you are ready! Come back when you have decided and reap the rewards.")
        await ctx.send(embed=embed)

    @explore.command()
    async def start(self, ctx, duration: int):
        """With this command you start an adventure.

        Arguments:
            ctx {var} -- context of the sent message.
            duration {int} -- Duration (in minutes) of how long you want your adventure to be.
        """
        # Firstly we check if the user is in an adventure.
        in_adventure = await is_in_adventure(
            database=self.bot.db, user_id=ctx.author.id)

        embed = discord.Embed(colour=0xDC143C)

        # If he is not in an adventure then we can assign him one otherwise he can't.
        if not in_adventure:
            await add_adventure(database=self.bot.db,
                                user_id=ctx.author.id, duration=duration)
            embed.add_field(name="Your adventure has started!",
                            value=f"Return in {duration} minutes to get your rewards.")
            embed.set_footer(
                text="Use \"f!explore status\" to get updated on the progress.")
        else:
            embed.add_field(name="Your adventure **hasn't** started!",
                            value="You are already in an adventure. You can use \"f!explore status\" to get updated.")

        await ctx.send(embed=embed)

    @explore.command()
    async def status(self, ctx):
        """This command shows the status of your command. ex. The time left.

        Arguments:
            ctx {var} -- The context of the sent message.
        """
        # We get all the information about the adventure through the database.
        adventure = await get_adventure_information(database=self.bot.db, user_id=ctx.author.id)

        # If they are not in an adventure then they cannot see the status.
        if adventure is None:
            embed = discord.Embed(
                title="You are not in an adventure! You can use \"f!explore start (duration)\" to start exploring!", colour=0xDC143C)
            return

        # Here we check if the adventure hasn't ended using (Current Time - Start of Adventure Time) and checking if it's less than the duration.
        if (time.time() - adventure["starttime"]) < adventure["duration"]:
            seconds_left = adventure["duration"] - \
                (time.time() - adventure["starttime"])

            # Using the time module we can get the hours, minutes and seconds left from the seconds.
            time_left = time.strftime("%H:%M:%S", time.gmtime(seconds_left))

            embed = discord.Embed(
                title=f'You are currently in a {int(adventure["duration"]/60)} minute adventure.', colour=0xDC143C)
            embed.add_field(name="Time Left:", value=time_left)
            await ctx.send(embed=embed)
            return
        else:
            # If it actually has ended then we calculate the prizes.
            money_gained = int(adventure["duration"] / 60) * 2
            xp_gained = int((adventure["duration"] / 60) * 1.5)
            fakemon_gained = "None"

            # We use the give_money function in order to make giving money easier.
            await give_money(database=self.bot.db, user_id=ctx.author.id, amount=money_gained)

            # Same thing happens with experience.
            await give_xp_to_fakemon(database=self.bot.db, user_id=ctx.author.id, amount=xp_gained)

            # We have a 50/50 chance of getting a Fakemon at the end of the adventure.
            if random.choice([True, False]) is True:
                fakemon = await get_random_fakemon(database=self.bot.db)
                fakemon_id = await add_fakemon_to_database(database=self.bot.db, owner_id=ctx.author.id, fakemon_name=fakemon["name"], starter=False)
                await add_fakemon_to_inventory(database=self.bot.db, owner_id=ctx.author.id, fakemon_id=fakemon_id)

                fakemon_gained = fakemon["name"]

            embed = discord.Embed(
                title=f'Your adventure has finished!', colour=0xDC143C)
            embed.add_field(name="Rewards:",
                            value=f"• Money: {money_gained}\n• EXP: {xp_gained}\n• Fakemon: {fakemon_gained}")
            await ctx.send(embed=embed)
            await remove_adventure(database=self.bot.db, user_id=ctx.author.id)


def setup(bot):
    bot.add_cog(Adventures(bot))
