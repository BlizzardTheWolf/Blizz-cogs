import discord
from discord.ext import commands, tasks
import json
import random
import asyncio

class TruthOrDare(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.truth_questions = []
        self.dare_questions = []
        self.wyr_questions = []
        self.load_questions()

    def load_questions(self):
        try:
            with open("truth_questions.json", "r") as truth_file:
                self.truth_questions = json.load(truth_file)
        except FileNotFoundError:
            print("truth_questions.json not found. Make sure the file exists and contains a list of truth questions.")
        
        try:
            with open("dare_questions.json", "r") as dare_file:
                self.dare_questions = json.load(dare_file)
        except FileNotFoundError:
            print("dare_questions.json not found. Make sure the file exists and contains a list of dare questions.")
        
        try:
            with open("wyr_questions.json", "r") as wyr_file:
                self.wyr_questions = json.load(wyr_file)
        except FileNotFoundError:
            print("wyr_questions.json not found. Make sure the file exists and contains a list of would you rather questions.")

    @commands.command()
    async def tod(self, ctx, category: str):
        """Get a random Truth, Dare, or Would You Rather question."""
        if category.lower() == "truth":
            question = random.choice(self.truth_questions)
        elif category.lower() == "dare":
            question = random.choice(self.dare_questions)
        elif category.lower() == "wyr":
            question = random.choice(self.wyr_questions)
        else:
            await ctx.send("Invalid category. Please choose 'truth', 'dare', or 'wyr'.")
            return

        embed = discord.Embed(title=f"{ctx.author.display_name}'s {category.capitalize()} Question", description=question, color=discord.Color.blurple())
        msg = await ctx.send(embed=embed)

        # Add a reaction to allow users to get a new question
        await msg.add_reaction("🔄")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == "🔄" and reaction.message.id == msg.id

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=120.0, check=check)
            await msg.clear_reactions()
        except asyncio.TimeoutError:
            await msg.clear_reactions()

def setup(bot):
    bot.add_cog(TruthOrDare(bot))
