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
        Cleanup the guild by deleting all channels and roles, keeping one category and renaming it, and creating a new channel with the specified name.
        """
        guild = ctx.guild

        # Delete all channels except the default one
        for channel in guild.channels:
            if not isinstance(channel, discord.CategoryChannel) and channel != ctx.channel:
                await channel.delete()

        # Delete all roles except @everyone
        for role in guild.roles:
            if role.name != "@everyone":
                await role.delete()

        # Find and rename the last remaining category
        categories = [category for category in guild.categories if category.name != category_name]
        for category in categories:
            await category.delete()
        
        # Create a new category with the specified name
        category = await guild.create_category(category_name)
        
        # Create a new text channel inside the category
        await guild.create_text_channel(channel_name, category=category)

        await ctx.send("Guild cleanup completed. Channels and roles have been deleted, and a new category and channel have been created.")

def setup(bot):
    bot.add_cog(CleanupGuild(bot))
