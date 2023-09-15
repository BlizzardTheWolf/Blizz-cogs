import discord
from redbot.core import commands

class AppealDM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def appeal(self, ctx, user: discord.User):
        """Send ban appeal form."""
        embed = discord.Embed(
            title='Ban appeal form for Joe Caine & Co',
            description='Click the link below for the form.\n\n[https://forms.gle/hm6EwyKdCFsn8opQA](https://forms.gle/hm6EwyKdCFsn8opQA)',
            colour=15158332,
        )

        embed.set_author(
            name='Joe Caine & Co',
            icon_url='https://images-ext-2.discordapp.net/external/WpNkZdR9ewGNudG8uTVXu33m-Yqo2qEVr5VZrA_hCcY/%3Fsize%3D1024/https/cdn.discordapp.com/icons/1090736013258789028/a_bc4b81914fd1795cbee691017a907c99.gif?width=1024&height=1024'
        )

        try:
            await user.send(embed=embed)
            await ctx.send(f"Ban appeal form has been sent to {user.name}.")
        except discord.Forbidden:
            await ctx.send("I couldn't send the appeal form. Make sure the user's DMs are open.")

def setup(bot):
    bot.add_cog(AppealDM(bot))
