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
    async def unafk(self, ctx):
        """Remove your AFK status."""
        user = ctx.author
        guild = ctx.guild

        is_afk = await self.is_afk(user.id, guild)

        if is_afk:
            await self.remove_afk(user.id, guild)
            await ctx.send(f"{user.mention} is no longer AFK.")
        else:
            await ctx.send(f"{user.mention} is not currently AFK.")

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

    @commands.command(hidden=True)
    @checks.mod_or_permissions(manage_guild=True)
    async def resetafk(self, ctx, user: discord.User):
        """Reset someone's AFK status."""
        guild = ctx.guild
        await self.remove_afk(user.id, guild)
        await ctx.send(f"Reset AFK status for {user.mention}.")

    @afksettings.command()
    async def setreset(self, ctx, value: bool):
        """Toggle whether mods can reset AFK status."""
        await self.config.guild(ctx.guild).mod_reset_enabled.set(value)
        await ctx.send(f"Mod AFK reset is {'enabled' if value else 'disabled'}.")
