import discord
from discord.ext import commands
import asyncio


class Locations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def set(self, ctx):
        embed = discord.Embed(colour=0xDC143C)
        embed.add_field(name="Set Event Locations",
                        value="You are able to set in which location you can see certain events. Use '!fset location (battles/wilderness) (@Channel)'.")
        await ctx.send(embed=embed)

    @set.command()
    @commands.has_permissions(administrator=True)
    async def location(self, ctx, event: str, channel: discord.TextChannel):
        if event.lower() not in ["wilderness", "battles"]:
            embed = discord.Embed(
                title="You can use either battles or wilderness as your event.", colour=0xDC143C)
            await ctx.send(embed=embed)
            return

        if event.lower() == "battles":
            await self.bot.db.execute('UPDATE channels SET battles = $1 WHERE server = $2', channel.id, ctx.guild.id)
        else:
            await self.bot.db.execute('UPDATE channels SET wilderness = $1 WHERE server = $2', channel.id, ctx.guild.id)

        embed = discord.Embed(
            title=f"You have set {channel.name} as your {event.lower()} channel.", colour=0xDC143C)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Locations(bot))
