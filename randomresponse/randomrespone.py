import discord
from redbot.core import commands, checks
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import box, pagify
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS

class RandomResponseCog(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot
        self.responses = []

    def get_response(self):
        return self.responses

    @commands.group()
    async def randomresponse(self, ctx):
        """Manage random responses."""
        pass

    @randomresponse.command(name="add")
    @checks.mod_or_permissions(manage_messages=True)
    async def add_response(self, ctx, *, response: str):
        """Add a response to the list of random responses."""
        self.responses.append(response)
        await ctx.send(f"Response added: `{response}`")

    @randomresponse.command(name="list")
    async def list_responses(self, ctx):
        """List all random responses."""
        if not self.responses:
            await ctx.send("No responses added yet.")
            return
        formatted_responses = "\n".join(f"{i + 1}. {response}" for i, response in enumerate(self.responses))
        response_pages = [box(page) for page in pagify(formatted_responses)]
        await menu(ctx, response_pages, DEFAULT_CONTROLS)

    @randomresponse.command(name="remove")
    @checks.mod_or_permissions(manage_messages=True)
    async def remove_response(self, ctx, response_number: int):
        """Remove a response from the list by its number."""
        if 1 <= response_number <= len(self.responses):
            removed_response = self.responses.pop(response_number - 1)
            await ctx.send(f"Response removed: `{removed_response}`")
        else:
            await ctx.send("Invalid response number. Use `[p]randomresponse list` to see response numbers.")

    @commands.command()
    async def joke(self, ctx):
        """Display a random response from the list."""
        if not self.responses:
            await ctx.send("No responses available.")
            return
        response = discord.utils.choice(self.responses)
        await ctx.send(response)

    @randomresponse.error
    async def randomresponse_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send("You don't have permission to use this command.")

def setup(bot: Red):
    cog = RandomResponseCog(bot)
    bot.add_cog(cog)
