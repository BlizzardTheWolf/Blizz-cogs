import discord
from redbot.core import commands

class AppealDM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def appeal(self, ctx, user: discord.User):
        """Send ban appeal form."""
        appeal_form = "Ban appeal form for Joe Caine & Co\n\nhttps://forms.gle/hm6EwyKdCFsn8opQA"
        try:
            await user.send(appeal_form)
            await ctx.send(f"Ban appeal form has been sent to {user.name}.")
        except discord.Forbidden:
            await ctx.send("I couldn't send the appeal form. Make sure the user's DMs are open.")

def setup(bot):
    bot.add_cog(AppealDM(bot))
