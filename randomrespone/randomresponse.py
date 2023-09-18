import discord
from discord.ext import commands
from redbot.core import Config
import random

class JokeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)  # Change identifier
        self.config.register_guild(responses=[])

    @commands.command()
    async def joke(self, ctx):
        """Display a random configured response."""
        responses = await self.config.guild(ctx.guild).responses()
        if not responses:
            await ctx.send("No responses configured.")
        else:
            response = random.choice(responses)
            await ctx.send(response)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def jokeadd(self, ctx, *new_responses: str):
        """Add new responses to the list."""
        current_responses = await self.config.guild(ctx.guild).responses()
        current_responses.extend(new_responses)
        await self.config.guild(ctx.guild).responses.set(current_responses)
        await ctx.send("Responses added successfully.")

    @jokeadd.error
    async def jokeadd_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You need the 'Manage Messages' permission to add responses.")

    @commands.command()
    async def jokelist(self, ctx):
        """List all configured responses."""
        responses = await self.config.guild(ctx.guild).responses()
        if not responses:
            await ctx.send("No responses configured.")
        else:
            response_list = "\n".join([f"{i+1}. {response}" for i, response in enumerate(responses)])
            await ctx.send(f"List of responses:\n{response_list}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def jokeremove(self, ctx, response_number: int):
        """Remove a response by its number."""
        responses = await self.config.guild(ctx.guild).responses()
        if response_number <= 0 or response_number > len(responses):
            await ctx.send("Invalid response number.")
        else:
            removed_response = responses.pop(response_number - 1)
            await self.config.guild(ctx.guild).responses.set(responses)
            await ctx.send(f"Response {response_number}: '{removed_response}' removed successfully.")

    @jokeremove.error
    async def jokeremove_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You need the 'Manage Messages' permission to remove responses.")

def setup(bot):
    bot.add_cog(JokeCog(bot))
