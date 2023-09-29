import discord
from redbot.core import commands, Config
import random
import json

class TruthOrDare(commands.Cog):
    """Truth or Dare Cog"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=5555567890)  # Use a unique identifier
        default_global = {
            "truth_questions": [],
            "dare_questions": [],
            "wyr_questions": []
        }
        self.config.register_global(**default_global)

        # Load questions from JSON files
        self.load_questions()

    def load_questions(self):
        try:
            with open("truth_questions.json", "r") as f:
                truth_questions = json.load(f)
                self.config.truth_questions.set(truth_questions)

            with open("dare_questions.json", "r") as f:
                dare_questions = json.load(f)
                self.config.dare_questions.set(dare_questions)

            with open("wyr_questions.json", "r") as f:
                wyr_questions = json.load(f)
                self.config.wyr_questions.set(wyr_questions)
        except FileNotFoundError:
            pass

    @commands.Cog.listener()
    async def on_ready(self):
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

        if not questions:
            await ctx.send(f"No {category} questions found.")
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
