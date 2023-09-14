import discord
from redbot.core import commands, Config
from redbot.core.utils import mod

class CaseList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)  # Replace with your unique identifier

    @commands.command()
    async def caselist(self, ctx, user: discord.User):
        mod_logs = await mod.get_modlogs(self.config, user.id)
        if not mod_logs:
            await ctx.send("No mod logs found for this user.")
            return

        embeds = []
        page_size = 5  # Adjust the number of cases per page as needed
        total_logs = 0

        for page_num, cases in enumerate(mod_logs, start=1):
            page_embed = discord.Embed(
                title=f"Modlogs for {user.display_name} (Page {page_num} of {len(mod_logs)})",
                color=discord.Color.blue(),
            )

            for case_num, case_data in enumerate(cases, start=1):
                case_reason = case_data["reason"]
                # Check if the reason is an automatic unmute (case insensitive)
                if "automatic unmute" not in case_reason.lower():
                    total_logs += 1
                    case_length = case_data["length"] if "length" in case_data else "N/A"

                    page_embed.add_field(
                        name=f"Case {case_num}",
                        value=(
                            f"Type: {case_data['type']}\n"
                            f"User: ({user.id}) {user.display_name}\n"
                            f"Moderator: {case_data['moderator']}\n"
                            f"Length: {case_length}\n"
                            f"Reason: {case_reason} - {case_data['date']}"
                        ),
                        inline=False,
                    )

                # Split into multiple embeds if necessary
                if case_num % page_size == 0:
                    embeds.append(page_embed)
                    page_embed = discord.Embed(
                        title=f"Modlogs for {user.display_name} (Page {page_num} of {len(mod_logs)})",
                        color=discord.Color.blue(),
                    )

            # Add the last page if it's not empty
            if page_embed.fields:
                embeds.append(page_embed)

        if not embeds:
            await ctx.send("No valid mod logs found for this user.")
            return

        current_page = 0
        message = await ctx.send(embed=embeds[current_page])
        if len(embeds) > 1:
            await message.add_reaction("◀")
            await message.add_reaction("▶")

            def check(reaction, user):
                return (
                    user == ctx.author
                    and reaction.message.id == message.id
                    and str(reaction.emoji) in ["◀", "▶"]
                )

            while True:
                try:
                    reaction, _ = await self.bot.wait_for("reaction_add", timeout=60, check=check)

                    if str(reaction.emoji) == "▶" and current_page < len(embeds) - 1:
                        current_page += 1
                    elif str(reaction.emoji) == "◀" and current_page > 0:
                        current_page -= 1

                    await message.edit(embed=embeds[current_page])
                    await message.remove_reaction(reaction, ctx.author)

                except TimeoutError:
                    break

        await message.clear_reactions()
