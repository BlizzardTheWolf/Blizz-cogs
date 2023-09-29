import discord
from redbot.core import commands, checks, Config
import random
import json
import asyncio

class TruthOrDare(commands.Cog):
    """Truth or Dare Cog"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)  # Change identifier
        self.config.init_custom("truth_questions",  # Custom config section for truth questions
                                3,  # Default question count
                                list)
        self.config.init_custom("dare_questions",   # Custom config section for dare questions
                                3,  # Default question count
                                list)
        self.config.init_custom("wyr_questions",    # Custom config section for would you rather questions
                                3,  # Default question count
                                list)

    async def initialize_questions(self):
        # Check if the config is empty, if so, initialize it with default questions
        if not await self.config.truth_questions():
            default_truth_questions = [
                "What's the most embarrassing thing that's happened to you?",
                "Have you ever lied to your best friend?",
                "What's your secret talent?"
            ]
            await self.config.truth_questions.set(default_truth_questions)

        if not await self.config.dare_questions():
            default_dare_questions = [
                "Do your best impersonation of a chicken for 1 minute.",
                "Call a random contact in your phone and sing 'Happy Birthday.'",
                "Wear socks on your hands for the next 5 minutes."
            ]
            await self.config.dare_questions.set(default_dare_questions)

        if not await self.config.wyr_questions():
            default_wyr_questions = [
                "Would you rather have the ability to fly or be invisible?",
                "Would you rather always be 10 minutes late or 20 minutes early?",
                "Would you rather live in a giant desert or a freezing tundra?"
            ]
            await self.config.wyr_questions.set(default_wyr_questions)

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

    @commands.command()
    @checks.is_owner()
    async def addquestion(self, ctx, category: str, *, question: str):
        """Add a new question to the specified category."""
        if category.lower() == "truth":
            config_section = "truth_questions"
        elif category.lower() == "dare":
            config_section = "dare_questions"
        elif category.lower() == "wyr":
            config_section = "wyr_questions"
        else:
            await ctx.send("Invalid category. Use 'truth', 'dare', or 'wyr'.")
            return

        questions = await self.config.custom(config_section, list)
        questions.append(question)
        await self.config.custom(config_section, list, value=questions)
        await ctx.send(f"New {category} question added.")

    @addquestion.error
    async def addquestion_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify a category and a question.")
        elif isinstance(error, checks.NotOwner):
            await ctx.send("Only the bot owner can add questions.")

    @commands.command()
    @checks.is_owner()
    async def removequestion(self, ctx, category: str, question_number: int):
        """Remove a question from the specified category by number."""
        if category.lower() == "truth":
            config_section = "truth_questions"
        elif category.lower() == "dare":
            config_section = "dare_questions"
        elif category.lower() == "wyr":
            config_section = "wyr_questions"
        else:
            await ctx.send("Invalid category. Use 'truth', 'dare', or 'wyr'.")
            return

        questions = await self.config.custom(config_section, list)
        if question_number <= 0 or question_number > len(questions):
            await ctx.send("Invalid question number.")
            return

        removed_question = questions.pop(question_number - 1)
        await self.config.custom(config_section, list, value=questions)
        await ctx.send(f"Question {question_number}: {removed_question} removed.")

    @removequestion.error
    async def removequestion_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify a category and a question number.")
        elif isinstance(error, checks.NotOwner):
            await ctx.send("Only the bot owner can remove questions.")

def setup(bot):
    cog = TruthOrDare(bot)
    bot.add_cog(cog)
