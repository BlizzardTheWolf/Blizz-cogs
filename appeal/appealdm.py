import discord
from discord.ext import commands

class AppealDM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="appeal")
    async def send_appeal(self, ctx, user: discord.User):
        appeal_form_link = "https://forms.gle/hm6EwyKdCFsn8opQA"
        
        embed = discord.Embed(
            title="Ban Appeal Form for Joe Caine & Co",
            description=f"Click [here]({appeal_form_link}) to access the ban appeal form.",
            color=discord.Color.purple()
        )
        
        await user.send(embed=embed)
        await ctx.send(f"Ban appeal form sent to {user.display_name}.")
