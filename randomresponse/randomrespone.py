import discord
from redbot.core import commands, checks, Config
from redbot.core.utils.chat_formatting import box, pagify
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
import random

class RandomResponseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)  # Change identifier
        self.config.register_guild(responses=[])

    @commands.group()
    @checks.mod_or_permissions(manage_messages=True)
    async def randomresponse(self, ctx):
        """Manage random responses."""
        pass

    @randomresponse.command(name="add")
    async def add_response(self, ctx, *, response: str):
        """Add a response to the list of random responses."""
        async with self.config.guild(ctx.guild).responses() as responses:
            responses.append(response)
        await ctx.send(f"Response added: `{response}`")

    @randomresponse.command(name="list")
    async def list_responses(self, ctx):
        """List all random responses."""
        responses = await self.config.guild(ctx.guild).responses()
        if not responses:
            await ctx.send("No responses added yet.")
            return
        formatted_responses = "\n".join(f"{i + 1}. {response}" for i, response in enumerate(responses))
        response_pages = [box(page) for page in pagify(formatted_responses)]
        await menu(ctx, response_pages, DEFAULT_CONTROLS)

    @randomresponse.command(name="remove")
    async def remove_response(self, ctx, response_number: int):
        """Remove a response from the list by its number."""
        async with self.config.guild(ctx.guild).responses() as responses:
            if 1 <= response_number <= len(responses):
                removed_response = responses.pop(response_number - 1)
                await ctx.send(f"Response removed: `{removed_response}`")
            else:
                await ctx.send("Invalid response number. Use `[p]randomresponse list` to see response numbers.")

    @commands.command()
    async def joke(self, ctx):
        """Display a random response from the list."""
        responses = await self.config.guild(ctx.guild).responses()
        if not responses:
            await ctx.send("No responses available.")
            return
        response = random.choice(responses)
        await ctx.send(response)

    @randomresponse.error
    async def randomresponse_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send("You don't have permission to use this command.")
