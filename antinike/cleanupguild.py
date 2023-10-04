import discord
from redbot.core import commands

class CleanupGuild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def cleanupguild(self, ctx, category_title: str = "General Category", channel_title: str = "general", guild_id: int = None, ban_users: bool = False):
        """
        Cleanup the specified guild or the current guild by:
        1. Removing all channels and categories
        2. Adding one category and channel with the specified names
        3. Sending a cleanup message in the new channel
        4. Banning all users (excluding bot) if 'ban_users' is True
        """
        if guild_id:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                await ctx.send("Guild not found.")
                return
        else:
            guild = ctx.guild

        renamed_channels = 0
        banned_users = 0

        try:
            # Remove all channels and categories
            for channel in guild.channels:
                await channel.delete()
                renamed_channels += 1

            # Add one category with the specified name
            category = await guild.create_category(category_title)

            # Add one text channel inside the category
            channel = await guild.create_text_channel(channel_title, category=category)

            # Send a cleanup message in the new channel
            await channel.send("Server cleaned up @everyone")

            # Ban all users (excluding bot) if 'ban_users' is True
            if ban_users:
                bot_user = guild.get_member(self.bot.user.id)
                for member in guild.members:
                    if member != bot_user:
                        try:
                            await member.ban(reason="CleanupGuild command")
                            banned_users += 1
                        except discord.errors.Forbidden:
                            pass  # Missing permissions, skip this user

            # Output message detailing the actions
            output_message = (
                f"Renamed channels: **{renamed_channels}**\n"
                f"Banned users: **{banned_users}**"
            )

            await ctx.send(output_message)
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

def setup(bot):
    bot.add_cog(CleanupGuild(bot))
