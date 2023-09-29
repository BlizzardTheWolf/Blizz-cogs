import discord
import random
from discord.ext import commands

class TruthOrDare(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.categories = {
            'truth': [],
            'dare': [],
            'wyr': []
        }
        self.current_game = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} cog has been loaded!')

    @commands.command(name='tod')
    async def truth_or_dare(self, ctx, category: str = None):
        if category is None:
            await ctx.send("Please specify a category: 'truth', 'dare', or 'wyr'.")
            return

        if category not in self.categories:
            await ctx.send("Invalid category. Choose from 'truth', 'dare', or 'wyr'.")
            return

        questions = self.categories[category]
        if not questions:
            await ctx.send(f"No {category} questions available. Please add some using `[p]tod add {category} <question>`.")
            return

        question = random.choice(questions)
        await ctx.send(f"**{ctx.author.display_name}**, {question}")

    @commands.command(name='todadd')
    @commands.is_owner()
    async def add_question(self, ctx, category: str, *, question: str):
        if category not in self.categories:
            await ctx.send("Invalid category. Choose from 'truth', 'dare', or 'wyr'.")
            return

        self.categories[category].append(question)
        await ctx.send(f"Added a new {category} question!")

def setup(bot):
    bot.add_cog(TruthOrDare(bot))
