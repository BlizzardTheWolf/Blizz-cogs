import discord
from discord.ext import commands, tasks
import asyncio
import random

# Define the Truth or Dare cog
class TruthOrDare(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.questions = {
            "truth": [
                "What is your biggest fear?",
                "Have you ever lied to a friend?",
                "What's the most embarrassing thing you've done in public?",
                "What's your guilty pleasure?",
                "What's a secret talent you have?",
                "Have you ever cheated on a test?",
                "What's something you've never told anyone?",
                "What's your most awkward date experience?",
                "Have you ever stolen something?",
                "What's a habit you want to break?"
            ],
            "dare": [
                "Do 10 push-ups.",
                "Sing a song in a silly voice.",
                "Call a friend and tell them a funny joke.",
                "Speak in an accent for the next round.",
                "Dance for 30 seconds.",
                "Send a random emoji to someone in your DMs.",
                "Tell a funny knock-knock joke.",
                "Draw a picture and share it in chat.",
                "Post a selfie with a funny caption.",
                "Tell a short, funny story."
            ],
            "would_you_rather": [
                "Would you rather have the ability to fly or be invisible?",
                "Would you rather live on the beach or in the mountains?",
                "Would you rather never use the internet again or never watch TV again?",
                "Would you rather have unlimited money but no friends or have great friends but very little money?",
                "Would you rather travel to the past or the future?",
                "Would you rather have the ability to read minds or teleport?",
                "Would you rather eat only pizza for a year or never eat pizza again?",
                "Would you rather be a famous actor or a successful entrepreneur?",
                "Would you rather always be hot or always be cold?",
                "Would you rather be a superhero with a secret identity or a famous celebrity?"
            ]
        }
        self.current_question_type = None
        self.current_question_index = 0
        self.current_question_list = []

    # Function to get the next question
    def get_next_question(self):
        if not self.current_question_list:
            return None
        if self.current_question_index < len(self.current_question_list) - 1:
            self.current_question_index += 1
            return self.current_question_list[self.current_question_index]
        else:
            return None

    # Function to send the next question
    async def send_next_question(self, ctx):
        next_question = self.get_next_question()
        if next_question:
            await ctx.send(f"**Question {self.current_question_index + 1}:** {next_question}")
        else:
            await ctx.send("No more questions in this category. Game over!")

    # Command to start a Truth or Dare game
    @commands.command()
    async def truthordare(self, ctx, question_type: str):
        if question_type not in self.questions:
            await ctx.send("Invalid question type. Choose from 'truth', 'dare', or 'wouldyourather'.")
            return

        self.current_question_type = question_type
        self.current_question_list = self.questions[question_type]
        random.shuffle(self.current_question_list)
        self.current_question_index = -1

        await self.send_next_question(ctx)
        # Add the :track_next: emote
        await ctx.message.add_reaction("⏭️")

        # Define a check function for the reaction event
        def check(reaction, user):
            return (
                user == ctx.author
                and str(reaction.emoji) == "⏭️"
                and reaction.message.id == ctx.message.id
            )

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            await ctx.message.clear_reaction("⏭️")
            await self.send_next_question(ctx)
        except asyncio.TimeoutError:
            await ctx.send("Time's up! Game over.")
            self.current_question_type = None

# Setup function to add the cog to the bot
def setup(bot):
    bot.add_cog(TruthOrDare(bot))
