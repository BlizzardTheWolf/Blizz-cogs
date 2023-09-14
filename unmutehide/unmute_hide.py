import discord
from redbot.core import commands, checks
from redbot.core.utils.chat_formatting import pagify
from typing import Optional

class UnmuteHideCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.mod_or_permissions(kick_members=True)  # Customize the required permissions as needed
    async def listcases(self, ctx, user: Optional[discord.Member] = None):
        """List moderation cases for a user."""
        # Fetch cases for the user (customize this logic as needed)
        cases = await self.get_cases(user)

        if not cases:
            await ctx.send("No cases found.")
            return

        # Filter out cases with reason "Automatic unmute"
        filtered_cases = [case for case in cases if case.reason != "Automatic unmute"]

        if not filtered_cases:
            await ctx.send("No cases found.")
            return

        # Display the filtered cases in a paginated format
        page_list = pagify(self.format_cases(filtered_cases))
        for page in page_list:
            await ctx.send(page)

    async def get_cases(self, user):
        # Replace this with your actual case fetching logic.
        # For demonstration purposes, we'll use a sample list of cases.
        sample_cases = [
            discord.MemberCase(case_id=1, action="Mute", reason="Rule violation"),
            discord.MemberCase(case_id=2, action="Ban", reason="Spamming"),
            discord.MemberCase(case_id=3, action="Unmute", reason="Automatic unmute"),
            discord.MemberCase(case_id=4, action="Kick", reason="Harassment"),
        ]

        # Fetch cases for the user (customize this logic as needed)
        return sample_cases

    def format_cases(self, cases):
        formatted_cases = []
        for case in cases:
            formatted_cases.append(f"Case #{case.case_id}: {case.action} - Reason: {case.reason}")
        return "\n".join(formatted_cases)

def setup(bot):
    bot.add_cog(UnmuteHideCog(bot))
