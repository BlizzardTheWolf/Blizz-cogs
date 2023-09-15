import discord
from redbot.core import commands

class AppealDM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def appeal(self, ctx, user: discord.User):
        """Send ban appeal form to the specified user's DMs."""
        try:
            embed = discord.Embed(
                title='Ban appeal form for Joe Caine & Co',
                description='Click the link below for the form.\n\nhttps://forms.gle/hm6EwyKdCFsn8opQA',
                colour=15158332,
                url='https://forms.gle/hm6EwyKdCFsn8opQA',
            )

            embed.set_author(
                name='Joe Caine & Co',
                icon_url='https://images-ext-2.discordapp.net/external/WpNkZdR9ewGNudG8uTVXu33m-Yqo2qEVr5VZrA_hCcY/%3Fsize%3D1024/https/cdn.discordapp.com/icons/1090736013258789028/a_bc4b81914fd1795cbee691017a907c99.gif?width=1024&height=1024'
            )

            await user.send(embed=embed)
            await ctx.send(f"Ban appeal form sent to {user.name}#{user.discriminator}")
        except discord.Forbidden:
            await ctx.send("I couldn't send a message to this user. Make sure their DMs are open or they share a server with me.")

def setup(bot):
    bot.add_cog(AppealDM(bot))
