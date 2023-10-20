import discord
from redbot.core import commands
from redbot.core.utils.chat_formatting import humanize_list

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk_statuses = {}  # Dictionary to store AFK statuses
        self.mod_roles = ["Moderator", "Admin"]  # Replace with your mod roles

    @commands.command()
    async def afk(self, ctx, *, reason: str = "AFK"):
        """Set your AFK status with an optional reason."""
        member = ctx.author
        self.afk_statuses[member.id] = reason
        await member.edit(nick=f"[AFK] {member.display_name}")
        await ctx.send(f"{ctx.author.mention} is now AFK: {reason}")

    @commands.Cog.listener()
    async def on_message(self, message):
        author = message.author
        if author.id in self.afk_statuses:
            del self.afk_statuses[author.id]  # Clear AFK status upon sending a message
            await author.edit(nick=author.display_name.lstrip("[AFK] "))

    @commands.Cog.listener()
    async def on_message_without_command(self, message):
        if message.mentions:
            afk_mentions = [
                member.mention for member in message.mentions if member.id in self.afk_statuses
            ]
            if afk_mentions:
                afk_list = humanize_list(afk_mentions)
                await message.channel.send(f"{afk_list} {'is' if len(afk_mentions) == 1 else 'are'} AFK.")

    @commands.command()
    @commands.has_any_role(*mod_roles)
    async def clearafk(self, ctx, member: discord.Member):
        """Clear the AFK status of a member."""
        if member.id in self.afk_statuses:
            del self.afk_statuses[member.id]
            await member.edit(nick=member.display_name.lstrip("[AFK] "))
            await ctx.send(f"AFK status cleared for {member.mention}.")

    @commands.command()
    @commands.has_any_role(*mod_roles)
    async def listafk(self, ctx):
        """List all members with AFK status."""
        afk_members = [ctx.guild.get_member(member_id) for member_id in self.afk_statuses.keys()]
        afk_members = [member.mention for member in afk_members if member]
        afk_list = humanize_list(afk_members) if afk_members else "No members are currently AFK."
        await ctx.send(f"Members with AFK status: {afk_list}")

def setup(bot):
    afk_cog = AFK(bot)
    bot.add_cog(afk_cog)
