import discord
from redbot.core import commands, Config

class AutoModCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=7320912352)
        self.config.register_global(message="This is your default automodded message.")

    @commands.command()
    async def setautomodded(self, ctx, *, message_content):
        """Set the message to send with the automodded command."""
        await self.config.message.set(message_content)
        await ctx.send("Automodded message has been updated.")

    @commands.command()
    async def automodded(self, ctx):
        """Send a direct message with the automodded message to the user who invoked this command."""
        user = ctx.message.author
        message_content = await self.config.message()
        try:
            await user.send(message_content)
            await ctx.send("Automodded message has been sent to you via DM.")
        except discord.Forbidden:
            await ctx.send("I couldn't send you a message. Make sure your DMs are enabled.")

def setup(bot):
    bot.add_cog(AutoModCog(bot))
