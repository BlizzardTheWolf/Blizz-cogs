import discord
from redbot.core import commands

class CleanupGuild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

        # Leave the server
        await guild.leave()

def setup(bot):
    bot.add_cog(CleanupGuild(bot))
