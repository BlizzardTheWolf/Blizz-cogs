from redbot.core import commands, Config
import discord

class ForwardChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890, force_registration=True)
        self.config.register_global(forwarding_rules=[])

    @commands.group()
    async def forward(self, ctx):
        """Manage forwarding rules."""
    
    @forward.command(name="list")
    async def list_forwarding_rules(self, ctx):
        forwarding_rules = await self.config.forwarding_rules()
        if not forwarding_rules:
            await ctx.send("No forwarding rules defined.")
        else:
            rules = "\n".join([f"{rule['id']}: {rule['from_channel']} -> {rule['to_channel']}" for rule in forwarding_rules])
            await ctx.send(f"Forwarding Rules:\n{rules}")

    @forward.command(name="remove")
    async def remove_forwarding_rule(self, ctx, rule_id: int):
        forwarding_rules = await self.config.forwarding_rules()
        rule = next((r for r in forwarding_rules if r['id'] == rule_id), None)
        if rule:
            forwarding_rules.remove(rule)
            await self.config.forwarding_rules.set(forwarding_rules)
            await ctx.send(f"Removed forwarding rule {rule_id}: {rule['from_channel']} -> {rule['to_channel']}")
        else:
            await ctx.send(f"Forwarding rule with ID {rule_id} not found.")

    @forward.command(name="add")
    async def add_forwarding_rule(self, ctx, from_channel: str, to_channel: str):
        forwarding_rules = await self.config.forwarding_rules()
        rule_id = len(forwarding_rules) + 1
        forwarding_rules.append({'id': rule_id, 'from_channel': from_channel, 'to_channel': to_channel})
        await self.config.forwarding_rules.set(forwarding_rules)
        await ctx.send(f"Added forwarding rule {rule_id}: {from_channel} -> {to_channel}")

    async def forward_message(self, message):
        forwarding_rules = await self.config.forwarding_rules()
        for rule in forwarding_rules:
            if message.channel.name == rule['from_channel']:
                to_channel = discord.utils.get(message.guild.text_channels, name=rule['to_channel'])
                if to_channel:
                    content = message.content
                    await to_channel.send(f"**Forwarded from {message.channel.name}**\n{content}")

def setup(bot):
    cog = ForwardChannel(bot)
    bot.add_cog(cog)
    bot.add_listener(cog.forward_message, "on_message")
