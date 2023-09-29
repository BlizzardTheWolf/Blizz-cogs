import discord
from redbot.core import commands
import random
import asyncio

class TruthOrDare(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.truth_questions = [
            "Have you ever cheated on a test?",
            "What is your most embarrassing childhood memory?",
            "What is your guilty pleasure TV show?"
        ]
        self.dare_questions = [
            "Do 10 push-ups right now.",
            "Sing a song in the voice channel.",
            "Text your crush 'I love you' (and let us know their response)."
        ]
        self.wyr_questions = [
            "Would you rather always be 10 minutes late or always 20 minutes early?",
            "Would you rather lose the ability to read or lose the ability to speak?",
            "Would you rather have the power of invisibility or the ability to fly?"
        ]

    @commands.command()
    async def tod(self, ctx, category: str):
        """Get a Truth, Dare, or Would You Rather question."""
        if category.lower() == "truth":
            question = random.choice(self.truth_questions)
        elif category.lower() == "dare":
            question = random.choice(self.dare_questions)
        elif category.lower() == "wyr":
            question = random.choice(self.wyr_questions)
        else:
            await ctx.send("Invalid category. Choose 'truth', 'dare', or 'wyr'.")
            return

        message = await ctx.send(f"**{category.capitalize()} Question:**\n{question}")
        await message.add_reaction("🔄")  # Add a reaction for refreshing questions

        def check(reaction, user):
            return (
                user == ctx.author
                and str(reaction.emoji) == "🔄"
                and reaction.message.id == message.id
            )

        try:
            reaction, _ = await self.bot.wait_for(
                "reaction_add", check=check, timeout=120.0
            )  # Wait for a reaction for up to 2 minutes
        except asyncio.TimeoutError:
            pass  # No reaction, do nothing
        else:
            # Remove old message and send a new one
            await message.delete()
            await self.tod(ctx, category)  # Send a new question

def setup(bot):
    bot.add_cog(TruthOrDare(bot))
