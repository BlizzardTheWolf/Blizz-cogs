import discord
from redbot.core import commands

class CleanupGuild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cleanupguild(self, ctx, channel_name: str = "general"):
        """
        Cleanup the guild by deleting all channels and roles, and creating a new channel with the specified name.
        """
        guild = ctx.guild

        # Delete all channels except the default one
        for channel in guild.channels:
            if not isinstance(channel, discord.CategoryChannel):
                await channel.delete()

        # Delete all roles except @everyone
        for role in guild.roles:
            if role.name != "@everyone":
                await role.delete()

        # Create a new text channel with the specified name
        await guild.create_text_channel(channel_name)

        await ctx.send("Guild cleanup completed. Channels and roles have been deleted, and a new channel has been created.")

def setup(bot):
    bot.add_cog(CleanupGuild(bot))
