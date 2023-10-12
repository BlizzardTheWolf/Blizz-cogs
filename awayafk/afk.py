import discord
from redbot.core import checks, commands, Config
import asyncio

class AFKCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=123456)
        default_guild_settings = {
            "afk_messages": {},
        }
        self.config.register_guild(**default_guild_settings)

    async def is_afk(self, user_id, guild):
        afk_messages = await self.config.guild(guild).afk_messages()
        return user_id in afk_messages

    async def set_afk(self, user_id, message, guild):
        afk_messages = await self.config.guild(guild).afk_messages()
        afk_messages[user_id] = message
        await self.config.guild(guild).afk_messages.set(afk_messages)

    async def remove_afk(self, user_id, guild):
        afk_messages = await self.config.guild(guild).afk_messages()
        if user_id in afk_messages:
            del afk_messages[user_id]
            await self.config.guild(guild).afk_messages.set(afk_messages)

    async def afk_on_message(self, message):
        user = message.author
        guild = message.guild

        if user.bot or not guild:
            return

        is_afk = await self.is_afk(user.id, guild)

        if is_afk:
            await self.remove_afk(user.id, guild)
            await message.channel.send(f"{user.mention} is no longer AFK.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild:
            await self.afk_on_message(message)

    @commands.command()
    async def afk(self, ctx, *, message: str = None):
        """Set yourself as AFK with an optional message."""
        user = ctx.author
        guild = ctx.guild

        if message:
            await self.set_afk(user.id, message, guild)
        else:
            await self.set_afk(user.id, "AFK", guild)

        await ctx.send(f"{user.mention} is now AFK. ({message})")

    @commands.command()
    async def clearafk(self, ctx, user: discord.User):
        """Clear someone's AFK status."""
        guild = ctx.guild
        await self.remove_afk(user.id, guild)
        await ctx.send(f"Cleared AFK status for {user.mention}.")

    @commands.command()
    async def afkonmessage(self, ctx, user: discord.User):
        """Set someone's AFK status as their default message."""
        user_id = user.id
        afk_messages = await self.config.guild(ctx.guild).afk_messages()
        if user_id in afk_messages:
            await self.set_afk(user.id, f"AFK: {afk_messages[user_id]}", ctx.guild)
            await ctx.send(f"Set {user.mention}'s AFK status as their default message.")
        else:
            await ctx.send(f"{user.mention} does not have an AFK status set.")

    @checks.admin_or_permissions(manage_guild=True)
    @commands.group()
    async def afksettings(self, ctx):
        """AFK settings for the server."""
        pass

    @afksettings.command()
    async def setping(self, ctx, value: bool):
        """Toggle whether pings should work for AFK users."""
        await self.config.guild(ctx.guild).ping_enabled.set(value)
        await ctx.send(f"AFK ping is {'enabled' if value else 'disabled'}.")

    @afksettings.command()
    async def setreset(self, ctx, value: bool):
        """Toggle whether mods can reset AFK status."""
        await self.config.guild(ctx.guild).mod_reset_enabled.set(value)
        await ctx.send(f"Mod AFK reset is {'enabled' if value else 'disabled'}.")

def setup(bot):
    bot.add_cog(AFKCog(bot))
