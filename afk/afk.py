import discord
from redbot.core import commands

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk_users = set()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id in self.afk_users:
            await self.clear_afk(message.author)
            await message.channel.send(f"{message.author.mention} is no longer AFK.")

    async def clear_afk(self, user):
        if user.id in self.afk_users:
            self.afk_users.remove(user.id)
            try:
                await user.edit(nick=user.display_name.replace("[AFK] ", ""))
            except discord.Forbidden:
                pass

    @commands.command()
    async def afk(self, ctx):
        if ctx.author.id not in self.afk_users:
            self.afk_users.add(ctx.author.id)
            try:
                await ctx.author.edit(nick=f"[AFK] {ctx.author.display_name}")
            except discord.Forbidden:
                pass
            await ctx.send(f"{ctx.author.mention} is now AFK.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id in self.afk_users:
            await self.clear_afk(message.author)
            await message.channel.send(f"{message.author.mention} is no longer AFK.")
            self.afk_users.discard(message.author.id)  # Clear AFK status

    @commands.command()
    async def notafk(self, ctx):
        await self.clear_afk(ctx.author)
        await ctx.send(f"{ctx.author.mention} is no longer AFK.")

def setup(bot):
    bot.add_cog(AFK(bot))
