import discord
import random
from discord.ext import commands, tasks

class TruthOrDare(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.truth_questions = [
            "What's the most embarrassing thing that happened to you in public?",
            "Have you ever cheated on a test?",
            "What's the last lie you told?",
        ]

        self.dare_questions = [
            "Do your best impression of a celebrity.",
            "Speak in an accent of your choice for the next minute.",
            "Dance for 30 seconds without music.",
        ]

        self.wyr_questions = [
            "Would you rather have the ability to fly or be invisible?",
            "Would you rather travel to the past or the future?",
            "Would you rather always speak your mind or never speak again?",
        ]

        self.current_question = None
        self.timer.stop()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} cog has been loaded!')

    def get_next_question(self, category):
        if category == 'truth':
            return random.choice(self.truth_questions)
        elif category == 'dare':
            return random.choice(self.dare_questions)
        elif category == 'wyr':
            return random.choice(self.wyr_questions)

    @commands.command(name='tod')
    async def truth_or_dare(self, ctx, category: str):
        if category not in ['truth', 'dare', 'wyr']:
            await ctx.send("Invalid category. Choose from 'truth', 'dare', or 'wyr'.")
            return

        if self.current_question is None:
            self.current_category = category
            self.current_question = self.get_next_question(category)
            self.current_question_msg = await ctx.send(f"**{ctx.author.display_name}**, {self.current_question}")
            await self.current_question_msg.add_reaction('➡️')
            self.timer.start(self.current_question_msg.author)
        else:
            await ctx.send("Someone is already playing Truth or Dare. Wait for the current question to finish.")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot or self.current_question is None:
            return

        if reaction.message.id == self.current_question_msg.id:
            if reaction.emoji == '➡️':
                new_question = self.get_next_question(self.current_category)
                await self.current_question_msg.edit(content=f"**{self.current_question_msg.author.display_name}**, {new_question}")
                self.timer.start(self.current_question_msg.author)

    @tasks.loop(seconds=60)
    async def timer(self, user):
        if self.current_question is not None:
            await self.current_question_msg.clear_reactions()
            await self.current_question_msg.add_reaction('❌')
            self.current_question = None

    @timer.before_loop
    async def before_timer(self):
        await self.bot.wait_until_ready()
