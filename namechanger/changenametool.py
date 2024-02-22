from redbot.core import commands

class ChangeName(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def changename(self, ctx, *, new_name: str):
        try:
            await ctx.author.edit(nick=new_name)
            await ctx.send(f"Your nickname has been changed to '{new_name}'")
        except commands.MissingPermissions:
            await ctx.send("Sorry, I don't have permission to change your nickname.")
