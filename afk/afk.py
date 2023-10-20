import discord
from redbot.core import commands
from asyncio import sleep
from collections import defaultdict

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk_users = defaultdict(int)

    async def clear_afk(self, user):
        if user.id in self.afk_users:
            if self.afk_users[user.id] <= 0:
                await user.edit(nick=user.display_name.replace("[AFK] ", ""))
                del self.afk_users[user.id]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id in self.afk_users:
            await self.clear_afk(message.author)
            await message.channel.send(f"{message.author.mention} is no longer AFK.")

    @commands.command()
    async def afk(self, ctx):
        if ctx.author.id not in self.afk_users:
            self.afk_users[ctx.author.id] = 0
            try:
                await ctx.author.edit(nick=f"[AFK] {ctx.author.display_name}")
            except discord.Forbidden:
                pass
            await ctx.send(f"{ctx.author.mention} is now AFK. Send another message to clear AFK status.")

def setup(bot):
    bot.add_cog(AFK(bot))
