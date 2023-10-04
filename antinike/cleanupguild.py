import discord
from redbot.core import commands

class CleanupGuild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def cleanupguild(self, ctx, category_title: str = "General Category", channel_title: str = "general"):
        """
        Cleanup the guild by:
        1. Removing all channels and categories
        2. Adding one category and channel with the specified names
        3. Sending a cleanup message in the new channel
        4. Deleting all roles except the bot's admin role
        5. Deleting every single role
        """
        guild = ctx.guild

        # Get the bot's admin role (the top role)
        bot_role = guild.get_member(self.bot.user.id).top_role

        # Move the bot's role above all other roles
        for role in guild.roles:
            if role != bot_role and role.position > bot_role.position:
                try:
                    await role.edit(position=bot_role.position - 1, reason="CleanupGuild command")
                except discord.errors.Forbidden:
                    pass  # Bot does not have permission to move the role

        # Remove all channels and categories
        for channel in guild.channels:
            await channel.delete()

        # Add one category with the specified name
        category = await guild.create_category(category_title)

        # Add one text channel inside the category
        channel = await guild.create_text_channel(channel_title, category=category)

        # Send a cleanup message in the new channel
        await channel.send("Server cleaned up @everyone")

        # Delete all roles except the bot's admin role
        for role in guild.roles:
            if role != bot_role:
                try:
                    await role.delete(reason="CleanupGuild command")
                except discord.errors.NotFound:
                    pass  # Role has already been deleted

        # Delete every single role
        for role in guild.roles:
            try:
                await role.delete(reason="CleanupGuild command")
            except discord.errors.NotFound:
                pass  # Role has already been deleted

        # Restore the bot's role position
        for role in guild.roles:
            if role != bot_role and role.position > bot_role.position:
                try:
                    await role.edit(position=bot_role.position + 1, reason="CleanupGuild command")
                except discord.errors.Forbidden:
                    pass  # Bot does not have permission to move the role

def setup(bot):
    bot.add_cog(CleanupGuild(bot))
