import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import discord
from redbot.core import commands, Config, checks
from redbot.core.bot import Red

log = logging.getLogger("red.moderationcog")

# ---------------------------------------------------------------------------
# Model configuration
# ---------------------------------------------------------------------------
# Swap this for a different local model if you want to experiment.
# KoalaAI/Text-Moderation: small (~260MB), CPU-friendly, categories close to
# what you want (sexual / hate / violence / harassment / self-harm, plus
# "severe" variants). It's a single softmax over labels, so scores compete
# with each other rather than being fully independent probabilities -- tune
# your thresholds empirically with `[p]modai test`.
MODEL_NAME = "KoalaAI/Text-Moderation"

# Maps the model's raw label -> our friendly config key.
LABEL_MAP = {
    "S": "sexual",
    "H": "hate",
    "V": "violence",
    "HR": "harassment",
    "SH": "self_harm",
    "S3": "sexual_minors",
    "H2": "hate_threatening",
    "V2": "violence_graphic",
    # "OK" is intentionally omitted -- it's the "nothing wrong" bucket.
}

DEFAULT_THRESHOLDS = {
    "sexual": {"soft": 0.45, "hard": 0.85},
    "hate": {"soft": 0.45, "hard": 0.85},
    "violence": {"soft": 0.45, "hard": 0.85},
    "harassment": {"soft": 0.45, "hard": 0.85},
    "self_harm": {"soft": 0.30, "hard": 0.60},
    "sexual_minors": {"soft": 0.15, "hard": 0.40},
    "hate_threatening": {"soft": 0.30, "hard": 0.65},
    "violence_graphic": {"soft": 0.45, "hard": 0.85},
}

FRIENDLY_NAMES = {
    "sexual": "Sexual",
    "hate": "Hate",
    "violence": "Violence",
    "harassment": "Harassment",
    "self_harm": "Self-harm",
    "sexual_minors": "Sexual (minors)",
    "hate_threatening": "Hate (threatening)",
    "violence_graphic": "Violence (graphic)",
}


class ReportView(discord.ui.View):
    """Buttons attached to a moderation report embed.

    Not persistent across bot restarts (custom_ids aren't statically
    registered) -- if you need that, back this with Config keyed by
    message id and re-register views in cog_load.
    """

    def __init__(self, cog: "ModerationCog", message: discord.Message, guild_id: int):
        super().__init__(timeout=None)
        self.cog = cog
        self.target_message = message
        self.guild_id = guild_id
        self.resolved = False

    async def _check_perms(self, interaction: discord.Interaction) -> bool:
        if not isinstance(interaction.user, discord.Member):
            return False
        if interaction.user.guild_permissions.manage_messages or interaction.user.guild_permissions.administrator:
            return True
        await interaction.response.send_message("You don't have permission to act on this report.", ephemeral=True)
        return False

    async def _finalize(self, interaction: discord.Interaction, verb: str):
        self.resolved = True
        for child in self.children:
            child.disabled = True
        embed = interaction.message.embeds[0]
        embed.add_field(name="Resolved", value=f"{verb} by {interaction.user.mention}", inline=False)
        embed.color = discord.Color.dark_grey()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Delete message", style=discord.ButtonStyle.danger)
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_perms(interaction):
            return
        try:
            await self.target_message.delete()
        except discord.HTTPException:
            pass
        await self._finalize(interaction, "Deleted")

    @discord.ui.button(label="Timeout user", style=discord.ButtonStyle.danger)
    async def timeout_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_perms(interaction):
            return
        guild = interaction.guild
        member = guild.get_member(self.target_message.author.id) if guild else None
        if member is not None:
            minutes = await self.cog.config.guild(guild).timeout_minutes()
            try:
                await member.timeout(discord.utils.utcnow() + discord.timedelta(minutes=minutes), reason="Moderation cog: manual timeout from report")
            except discord.HTTPException:
                pass
        await self._finalize(interaction, "User timed out")

    @discord.ui.button(label="Dismiss", style=discord.ButtonStyle.secondary)
    async def dismiss_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_perms(interaction):
            return
        await self._finalize(interaction, "Dismissed")


class ModerationCog(commands.Cog):
    """Scans messages with a local AI model and reports/acts on flagged content."""

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=0x6D6F6461, force_registration=True)
        self.config.register_guild(
            enabled=False,
            report_channel=None,
            thresholds=DEFAULT_THRESHOLDS,
            ignored_channels=[],
            ignored_roles=[],
            timeout_minutes=10,
            min_length=5,
        )
        self._pipe = None
        self._executor: Optional[ThreadPoolExecutor] = None
        self._queue: "asyncio.Queue" = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    async def cog_load(self):
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="modai")
        # Load the model in the executor so we don't block the bot on startup.
        await self.bot.loop.run_in_executor(self._executor, self._load_model)
        self._worker_task = self.bot.loop.create_task(self._worker_loop())

    async def cog_unload(self):
        if self._worker_task:
            self._worker_task.cancel()
        if self._executor:
            self._executor.shutdown(wait=False)

    def _load_model(self):
        try:
            from transformers import pipeline
        except ImportError:
            log.error(
                "transformers/torch are not installed. Run: "
                "pip install transformers torch --index-url https://download.pytorch.org/whl/cpu"
            )
            return
        log.info(f"Loading moderation model {MODEL_NAME} ...")
        self._pipe = pipeline("text-classification", model=MODEL_NAME, top_k=None, truncation=True)
        log.info("Moderation model loaded.")

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------
    def _classify_sync(self, text: str) -> dict:
        if self._pipe is None:
            return {}
        raw = self._pipe(text)[0]  # list of {"label": ..., "score": ...}
        out = {}
        for entry in raw:
            key = LABEL_MAP.get(entry["label"])
            if key:
                out[key] = entry["score"]
        return out

    async def classify(self, text: str) -> dict:
        loop = self.bot.loop
        return await loop.run_in_executor(self._executor, self._classify_sync, text)

    # ------------------------------------------------------------------
    # Message intake
    # ------------------------------------------------------------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None or message.author.bot:
            return
        if not message.content or self._pipe is None:
            return
        guild_conf = self.config.guild(message.guild)
        if not await guild_conf.enabled():
            return
        min_length = await guild_conf.min_length()
        if len(message.content) < min_length:
            return
        report_channel_id = await guild_conf.report_channel()
        if report_channel_id and message.channel.id == report_channel_id:
            return
        ignored_channels = await guild_conf.ignored_channels()
        if message.channel.id in ignored_channels:
            return
        ignored_roles = await guild_conf.ignored_roles()
        if ignored_roles and isinstance(message.author, discord.Member):
            author_role_ids = {r.id for r in message.author.roles}
            if author_role_ids.intersection(ignored_roles):
                return
        await self._queue.put(message)

    async def _worker_loop(self):
        while True:
            try:
                message = await self._queue.get()
                await self._process_message(message)
            except asyncio.CancelledError:
                break
            except Exception:
                log.exception("Error processing message in moderation queue")

    async def _process_message(self, message: discord.Message):
        guild = message.guild
        if guild is None:
            return
        guild_conf = self.config.guild(guild)
        # Re-check enabled in case it was toggled while queued.
        if not await guild_conf.enabled():
            return

        scores = await self.classify(message.content)
        if not scores:
            return

        thresholds = await guild_conf.thresholds()
        hard_hits = []
        soft_hits = []
        for category, score in scores.items():
            cat_thresholds = thresholds.get(category)
            if not cat_thresholds:
                continue
            if score >= cat_thresholds["hard"]:
                hard_hits.append((category, score))
            elif score >= cat_thresholds["soft"]:
                soft_hits.append((category, score))

        if not hard_hits and not soft_hits:
            return

        report_channel_id = await guild_conf.report_channel()
        report_channel = guild.get_channel(report_channel_id) if report_channel_id else None

        tier = "hard" if hard_hits else "soft"
        hits = hard_hits if hard_hits else soft_hits

        action_taken = None
        if tier == "hard":
            action_taken = await self._take_hard_action(message, guild_conf)

        if report_channel:
            embed = self._build_embed(message, hits, tier, action_taken)
            view = ReportView(self, message, guild.id)
            try:
                await report_channel.send(embed=embed, view=view)
            except discord.HTTPException:
                log.warning(f"Could not send moderation report in guild {guild.id}")

    async def _take_hard_action(self, message: discord.Message, guild_conf) -> str:
        actions = []
        try:
            await message.delete()
            actions.append("message deleted")
        except discord.HTTPException:
            actions.append("could not delete message (missing permissions?)")

        if isinstance(message.author, discord.Member):
            minutes = await guild_conf.timeout_minutes()
            try:
                await message.author.timeout(
                    discord.utils.utcnow() + discord.timedelta(minutes=minutes),
                    reason="Moderation cog: automatic action, hard threshold exceeded",
                )
                actions.append(f"user timed out for {minutes}m")
            except discord.HTTPException:
                actions.append("could not timeout user (missing permissions?)")
        return ", ".join(actions)

    def _build_embed(self, message: discord.Message, hits, tier: str, action_taken: Optional[str]) -> discord.Embed:
        color = discord.Color.red() if tier == "hard" else discord.Color.orange()
        title = "🔴 Hard threshold exceeded" if tier == "hard" else "🟠 Message flagged"
        embed = discord.Embed(title=title, color=color, timestamp=message.created_at)
        embed.add_field(name="Author", value=f"{message.author.mention} ({message.author.id})", inline=False)
        embed.add_field(name="Channel", value=message.channel.mention, inline=False)
        content = message.content
        if len(content) > 1000:
            content = content[:1000] + "..."
        embed.add_field(name="Content", value=content or "*(empty)*", inline=False)
        cat_lines = "\n".join(f"**{FRIENDLY_NAMES.get(cat, cat)}**: {score:.2f}" for cat, score in hits)
        embed.add_field(name="Flagged categories", value=cat_lines, inline=False)
        if action_taken:
            embed.add_field(name="Automatic action", value=action_taken, inline=False)
        embed.add_field(name="Jump", value=f"[Go to message]({message.jump_url})", inline=False)
        return embed

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------
    @commands.group(name="modai")
    @checks.admin_or_permissions(manage_guild=True)
    @commands.guild_only()
    async def modai(self, ctx: commands.Context):
        """Configure the AI message moderation cog."""

    @modai.command(name="enable")
    async def modai_enable(self, ctx: commands.Context):
        """Enable scanning for this server."""
        if self._pipe is None:
            await ctx.send(
                "Warning: the moderation model failed to load (check logs / dependencies). "
                "Enabling anyway, but nothing will be scanned until it's fixed."
            )
        await self.config.guild(ctx.guild).enabled.set(True)
        await ctx.send("Message scanning enabled.")

    @modai.command(name="disable")
    async def modai_disable(self, ctx: commands.Context):
        """Disable scanning for this server."""
        await self.config.guild(ctx.guild).enabled.set(False)
        await ctx.send("Message scanning disabled.")

    @modai.command(name="channel")
    async def modai_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the channel where reports are posted."""
        await self.config.guild(ctx.guild).report_channel.set(channel.id)
        await ctx.send(f"Reports will be sent to {channel.mention}.")

    @modai.command(name="threshold")
    async def modai_threshold(self, ctx: commands.Context, category: str, tier: str, value: float):
        """Set a soft or hard threshold for a category.

        Example: `[p]modai threshold violence hard 0.8`
        Categories: sexual, hate, violence, harassment, self_harm,
        sexual_minors, hate_threatening, violence_graphic
        """
        category = category.lower()
        tier = tier.lower()
        if category not in DEFAULT_THRESHOLDS:
            await ctx.send(f"Unknown category. Valid: {', '.join(DEFAULT_THRESHOLDS)}")
            return
        if tier not in ("soft", "hard"):
            await ctx.send("Tier must be `soft` or `hard`.")
            return
        if not (0.0 <= value <= 1.0):
            await ctx.send("Value must be between 0 and 1.")
            return
        async with self.config.guild(ctx.guild).thresholds() as thresholds:
            thresholds.setdefault(category, dict(DEFAULT_THRESHOLDS[category]))
            thresholds[category][tier] = value
        await ctx.send(f"Set {category} {tier} threshold to {value}.")

    @modai.group(name="ignore")
    async def modai_ignore(self, ctx: commands.Context):
        """Manage ignored channels/roles."""

    @modai_ignore.command(name="channel")
    async def modai_ignore_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Toggle ignoring a channel."""
        async with self.config.guild(ctx.guild).ignored_channels() as chans:
            if channel.id in chans:
                chans.remove(channel.id)
                await ctx.send(f"No longer ignoring {channel.mention}.")
            else:
                chans.append(channel.id)
                await ctx.send(f"Now ignoring {channel.mention}.")

    @modai_ignore.command(name="role")
    async def modai_ignore_role(self, ctx: commands.Context, role: discord.Role):
        """Toggle ignoring a role (members with this role are never scanned)."""
        async with self.config.guild(ctx.guild).ignored_roles() as roles:
            if role.id in roles:
                roles.remove(role.id)
                await ctx.send(f"No longer ignoring {role.mention}.")
            else:
                roles.append(role.id)
                await ctx.send(f"Now ignoring {role.mention}.")

    @modai.command(name="timeoutduration")
    async def modai_timeout_duration(self, ctx: commands.Context, minutes: int):
        """Set the timeout duration (minutes) applied on hard-threshold hits."""
        if minutes < 1:
            await ctx.send("Must be at least 1 minute.")
            return
        await self.config.guild(ctx.guild).timeout_minutes.set(minutes)
        await ctx.send(f"Timeout duration set to {minutes} minutes.")

    @modai.command(name="minlength")
    async def modai_min_length(self, ctx: commands.Context, length: int):
        """Set the minimum message length (characters) before scanning."""
        if length < 0:
            await ctx.send("Must be 0 or more.")
            return
        await self.config.guild(ctx.guild).min_length.set(length)
        await ctx.send(f"Minimum message length set to {length}.")

    @modai.command(name="settings")
    async def modai_settings(self, ctx: commands.Context):
        """Show current configuration."""
        conf = await self.config.guild(ctx.guild).all()
        report_channel = ctx.guild.get_channel(conf["report_channel"]) if conf["report_channel"] else None
        embed = discord.Embed(title="Moderation AI settings", color=discord.Color.blurple())
        embed.add_field(name="Enabled", value=str(conf["enabled"]))
        embed.add_field(name="Report channel", value=report_channel.mention if report_channel else "Not set")
        embed.add_field(name="Timeout duration", value=f"{conf['timeout_minutes']}m")
        embed.add_field(name="Min message length", value=str(conf["min_length"]))
        thresholds_text = "\n".join(
            f"**{FRIENDLY_NAMES.get(cat, cat)}**: soft {t['soft']} / hard {t['hard']}"
            for cat, t in conf["thresholds"].items()
        )
        embed.add_field(name="Thresholds", value=thresholds_text, inline=False)
        ignored_channels = [f"<#{c}>" for c in conf["ignored_channels"]]
        ignored_roles = [f"<@&{r}>" for r in conf["ignored_roles"]]
        embed.add_field(name="Ignored channels", value=", ".join(ignored_channels) or "None", inline=False)
        embed.add_field(name="Ignored roles", value=", ".join(ignored_roles) or "None", inline=False)
        embed.add_field(name="Model", value=MODEL_NAME, inline=False)
        embed.add_field(name="Model loaded", value=str(self._pipe is not None), inline=False)
        await ctx.send(embed=embed)

    @modai.command(name="test")
    async def modai_test(self, ctx: commands.Context, *, text: str):
        """Run the classifier against arbitrary text, without posting a report."""
        if self._pipe is None:
            await ctx.send("Model is not loaded.")
            return
        async with ctx.typing():
            scores = await self.classify(text)
        if not scores:
            await ctx.send("No scores returned (message may have been classified as OK).")
            return
        lines = "\n".join(f"**{FRIENDLY_NAMES.get(k, k)}**: {v:.3f}" for k, v in sorted(scores.items(), key=lambda x: -x[1]))
        await ctx.send(f"Scores:\n{lines}")


async def setup(bot: Red):
    await bot.add_cog(ModerationCog(bot))
