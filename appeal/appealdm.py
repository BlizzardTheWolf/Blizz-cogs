import discord
from redbot.core import commands

class AppealDM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def appeal(self, ctx, user: discord.User):
        """Send ban appeal form."""
        embed = discord.Embed(
            title="Ban Appeal Form",
            description="Click the link below to access the ban appeal form.",
            url="https://forms.gle/hm6EwyKdCFsn8opQA",
            color=discord.Color.red(),
        )
        try:
            await user.send(embed=embed)
            await ctx.send(f"Ban appeal form has been sent to {user.name}.")
        except discord.Forbidden:
            await ctx.send("I couldn't send the appeal form. Make sure the user's DMs are open.")

def setup(bot):
    bot.add_cog(AppealDM(bot))
