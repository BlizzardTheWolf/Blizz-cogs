import discord
from redbot.core import commands, checks
import random
import json
import asyncio

class TruthOrDare(commands.Cog):
    """Truth or Dare Cog"""

    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config

    async def initialize_questions(self):
        # Check if the JSON files exist, if not, initialize them with default questions
        default_truth_questions = [
            "What's the most embarrassing thing that's happened to you?",
            "Have you ever lied to your best friend?",
            "What's your secret talent?"
        ]
        default_dare_questions = [
            "Do your best impersonation of a chicken for 1 minute.",
            "Call a random contact in your phone and sing 'Happy Birthday.'",
            "Wear socks on your hands for the next 5 minutes."
        ]
        default_wyr_questions = [
            "Would you rather have the ability to fly or be invisible?",
            "Would you rather always be 10 minutes late or 20 minutes early?",
            "Would you rather live in a giant desert or a freezing tundra?"
        ]

        await self.config.truth_questions.set(default_truth_questions)
        await self.config.dare_questions.set(default_dare_questions)
        await self.config.wyr_questions.set(default_wyr_questions)

    async def cog_check(self, ctx):
        return ctx.guild is not None

    @commands.Cog.listener()
    async def on_ready(self):
        await self.initialize_questions()
        print("TruthOrDare cog is ready!")

    @commands.command()
    async def tod(self, ctx, category: str):
        """Get a random truth, dare, or would you rather question."""
        if category.lower() == "truth":
            questions = await self.config.truth_questions()
        elif category.lower() == "dare":
            questions = await self.config.dare_questions()
        elif category.lower() == "wyr":
            questions = await self.config.wyr_questions()
        else:
            await ctx.send("Invalid category. Use 'truth', 'dare', or 'wyr'.")
            return

        question = random.choice(questions)
        await ctx.send(f"{ctx.author.mention}, here's your {category} question: {question}")

    @tod.error
    async def tod_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify a category: 'truth', 'dare', or 'wyr'.")

def setup(bot):
    cog = TruthOrDare(bot)
    bot.add_cog(cog)
