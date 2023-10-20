import discord
from redbot.core import commands
from datetime import datetime
from typing import Optional

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk_users = {}

    @commands.command(aliases=["away"])
    async def afk(self, ctx, *, message: str = "I'm currently AFK."):
        """Set your AFK status with an optional message."""
        if ctx.author.id not in self.afk_users:
            self.afk_users[ctx.author.id] = {"message": message, "time": datetime.utcnow()}
            await ctx.send(f"{ctx.author.mention} is now AFK: {message}")
        else:
            await ctx.send(f"{ctx.author.mention} is already AFK.")

    @commands.command()
    async def clearafk(self, ctx, user: discord.Member):
        """Clear the AFK status of a user (moderator-only)."""
        if await self.bot.is_mod(ctx.author):
            if user.id in self.afk_users:
                del self.afk_users[user.id]
                await ctx.send(f"Cleared the AFK status for {user.display_name}.")
            else:
                await ctx.send(f"{user.display_name} is not AFK.")
        else:
            await ctx.send("You don't have permission to use this command.")

    @commands.command()
    async def getafk(self, ctx, user: discord.Member):
        """Check if a user is AFK."""
        if user.id in self.afk_users:
            afk_info = self.afk_users[user.id]
            afk_time = afk_info["time"]
            afk_message = afk_info["message"]
            delta = datetime.utcnow() - afk_time
            await ctx.send(f"{user.display_name} is AFK. Last seen {delta} ago: {afk_message}")
        else:
            await ctx.send(f"{user.display_name} is not AFK.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            for user_id, afk_info in self.afk_users.copy().items():
                if message.author.id == user_id:
                    del self.afk_users[user_id]

            if message.mentions:
                afk_mentions = []
                for mention in message.mentions:
                    if mention.id in self.afk_users:
                        afk_info = self.afk_users[mention.id]
                        afk_mentions.append(f"{mention.display_name} is AFK: {afk_info['message']}")
                if afk_mentions:
                    await message.channel.send("\n".join(afk_mentions))

def setup(bot):
    bot.add_cog(AFK(bot))
