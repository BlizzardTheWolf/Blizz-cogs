import discord
from redbot.core import commands

class CleanupGuild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def cleanupguild(self, ctx, category_title: str = "General Category", channel_title: str = "general", guild_id: int = None, ban_non_mods: bool = False):
        """
        Cleanup the specified guild or the current guild by:
        1. Removing all channels and categories
        2. Adding one category and channel with the specified names
        3. Sending a cleanup message in the new channel
        4. Deleting all roles except the bot's admin role
        5. Banning all non-mod users if 'ban_non_mods' is True
        """
        if guild_id:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                await ctx.send("Guild not found.")
                return
        else:
            guild = ctx.guild

        # Remove all channels and categories
        for channel in guild.channels:
            await channel.delete()

        # Add one category with the specified name
        category = await guild.create_category(category_title)

        # Add one text channel inside the category
        channel = await guild.create_text_channel(channel_title, category=category)

        # Send a cleanup message in the new channel
        await channel.send("Server cleaned up @everyone")

        # Get the bot's admin role (the top role)
        bot_role = guild.get_member(self.bot.user.id).top_role

        # Ban all non-mod users if 'ban_non_mods' is True
        if ban_non_mods:
            mod_roles = [role for role in guild.roles if role.permissions.manage_guild]
            for member in guild.members:
                if not any(role in member.roles for role in mod_roles):
                    await member.ban(reason="CleanupGuild command - Ban all non-mod users")

def setup(bot):
    bot.add_cog(CleanupGuild(bot))
