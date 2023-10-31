import discord
from discord.ext import commands
from discord.ext.commands import Cog, command

class ForwardChannel(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.forwarding_rules = []

    @command()
    async def forward(self, ctx, action, *args):
        if action == 'list':
            await self.list_forwarding_rules(ctx)
        elif action == 'remove':
            await self.remove_forwarding_rule(ctx, args)
        elif action == 'add':
            await self.add_forwarding_rule(ctx, args)
        else:
            await ctx.send("Invalid action. Use 'list', 'remove', or 'add'.")

    async def list_forwarding_rules(self, ctx):
        if not self.forwarding_rules:
            await ctx.send("No forwarding rules defined.")
        else:
            rules = "\n".join([f"{rule['id']}: {rule['from_channel']} -> {rule['to_channel']}" for rule in self.forwarding_rules])
            await ctx.send(f"Forwarding Rules:\n{rules}")

    async def remove_forwarding_rule(self, ctx, args):
        if not args:
            await ctx.send("Please provide the ID of the forwarding rule to remove.")
            return

        rule_id = args[0]
        rule_id = int(rule_id) if rule_id.isdigit() else None

        if rule_id is not None:
            rule = next((r for r in self.forwarding_rules if r['id'] == rule_id), None)
            if rule:
                self.forwarding_rules.remove(rule)
                await ctx.send(f"Removed forwarding rule {rule_id}: {rule['from_channel']} -> {rule['to_channel']}")
            else:
                await ctx.send(f"Forwarding rule with ID {rule_id} not found.")
        else:
            await ctx.send("Invalid rule ID.")

    async def add_forwarding_rule(self, ctx, args):
        if len(args) != 2:
            await ctx.send("Usage: [p]forward add <channel to copy from> <channel to copy to>")
            return

        from_channel_name, to_channel_name = args

        from_channel = discord.utils.get(ctx.guild.text_channels, name=from_channel_name)
        to_channel = discord.utils.get(ctx.guild.text_channels, name=to_channel_name)

        if from_channel and to_channel:
            rule_id = len(self.forwarding_rules) + 1
            self.forwarding_rules.append({'id': rule_id, 'from_channel': from_channel_name, 'to_channel': to_channel_name})
            await ctx.send(f"Added forwarding rule {rule_id}: {from_channel_name} -> {to_channel_name}")
        else:
            await ctx.send("One or both of the specified channels do not exist.")
