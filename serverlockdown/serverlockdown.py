import discord
from discord.ext import commands
from core import checks
from core.models import PermissionLevel
import asyncio
from datetime import datetime, timedelta

class ServerLockdown(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def lockdown(self, ctx: commands.Context):
        """
        Server lockdown command group.
        """
        await ctx.send_help(ctx.command)

    @lockdown.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def start(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """
        Start the lockdown - prevents members from sending messages in the specified channel (or all channels if none is specified).
        """
        if channel:
            await self._lockdown_channel(channel)
            await ctx.send(f"🔒 | The channel {channel.mention} has been locked down.")
        else:
            await self._lockdown(ctx.guild)
            await ctx.send("🔒 | The server has been locked down. Members cannot send messages in any channel.")

    @lockdown.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def end(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """
        End the lockdown - restores message permissions in the specified channel (or all channels if none is specified).
        """
        if channel:
            await self._end_lockdown_channel(channel)
            await ctx.send(f"🔓 | The channel {channel.mention} has been unlocked.")
        else:
            await self._end_lockdown(ctx.guild)
            await ctx.send("🔓 | The server lockdown has been lifted. Members can send messages again.")

    @lockdown.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def schedule_start(self, ctx: commands.Context, time: str, channel: discord.TextChannel = None):
        """
        Schedule a lockdown to start at a specific time (format: HH:MM 24-hour format) for a specific channel (or all channels if none is specified).
        """
        try:
            lockdown_time = datetime.strptime(time, "%H:%M").time()
            now = datetime.now().time()

            if lockdown_time > now:
                time_delta = datetime.combine(datetime.today(), lockdown_time) - datetime.combine(datetime.today(), now)
            else:
                time_delta = datetime.combine(datetime.today() + timedelta(days=1), lockdown_time) - datetime.combine(datetime.today(), now)

            await ctx.send(f"⏰ | Lockdown scheduled to start at {lockdown_time} (in {time_delta}).")
            await asyncio.sleep(time_delta.total_seconds())

            if channel:
                await self._lockdown_channel(channel)
                await ctx.send(f"🔒 | The channel {channel.mention} has been locked down.")
            else:
                await self._lockdown(ctx.guild)
                await ctx.send("🔒 | The server has been locked down.")
        
        except ValueError:
            await ctx.send("❌ | Invalid time format. Please use HH:MM (24-hour format).")

    @lockdown.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def schedule_end(self, ctx: commands.Context, time: str, channel: discord.TextChannel = None):
        """
        Schedule a lockdown to end at a specific time (format: HH:MM 24-hour format) for a specific channel (or all channels if none is specified).
        """
        try:
            end_time = datetime.strptime(time, "%H:%M").time()
            now = datetime.now().time()

            if end_time > now:
                time_delta = datetime.combine(datetime.today(), end_time) - datetime.combine(datetime.today(), now)
            else:
                time_delta = datetime.combine(datetime.today() + timedelta(days=1), end_time) - datetime.combine(datetime.today(), now)

            await ctx.send(f"⏰ | Lockdown scheduled to end at {end_time} (in {time_delta}).")
            await asyncio.sleep(time_delta.total_seconds())

            if channel:
                await self._end_lockdown_channel(channel)
                await ctx.send(f"🔓 | The channel {channel.mention} has been unlocked.")
            else:
                await self._end_lockdown(ctx.guild)
                await ctx.send("🔓 | The server lockdown has been lifted.")
        
        except ValueError:
            await ctx.send("❌ | Invalid time format. Please use HH:MM (24-hour format).")

    @lockdown.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def schedule_both(self, ctx: commands.Context, start_time: str, end_time: str, channel: discord.TextChannel = None):
        """
        Schedule both a lockdown start and end (start: HH:MM, end: HH:MM) for a specific channel (or all channels if none is specified).
        """
        try:
            start_lockdown_time = datetime.strptime(start_time, "%H:%M").time()
            end_lockdown_time = datetime.strptime(end_time, "%H:%M").time()
            now = datetime.now().time()

            if start_lockdown_time > now:
                start_delta = datetime.combine(datetime.today(), start_lockdown_time) - datetime.combine(datetime.today(), now)
            else:
                start_delta = datetime.combine(datetime.today() + timedelta(days=1), start_lockdown_time) - datetime.combine(datetime.today(), now)

            if end_lockdown_time > now:
                end_delta = datetime.combine(datetime.today(), end_lockdown_time) - datetime.combine(datetime.today(), now)
            else:
                end_delta = datetime.combine(datetime.today() + timedelta(days=1), end_lockdown_time) - datetime.combine(datetime.today(), now)

            await ctx.send(f"⏰ | Lockdown scheduled to start at {start_lockdown_time}.")
            await asyncio.sleep(start_delta.total_seconds())

            if channel:
                await self._lockdown_channel(channel)
                await ctx.send(f"🔒 | The channel {channel.mention} has been locked down.")
            else:
                await self._lockdown(ctx.guild)
                await ctx.send("🔒 | The server has been locked down.")

            await ctx.send(f"⏰ | Lockdown scheduled to end at {end_lockdown_time}.")
            await asyncio.sleep(end_delta.total_seconds())

            if channel:
                await self._end_lockdown_channel(channel)
                await ctx.send(f"🔓 | The channel {channel.mention} has been unlocked.")
            else:
                await self._end_lockdown(ctx.guild)
                await ctx.send("🔓 | The server lockdown has been lifted.")
        
        except ValueError:
            await ctx.send("❌ | Invalid time format. Please use HH:MM (24-hour format).")

    # Helper function to lockdown the entire server
    async def _lockdown(self, guild: discord.Guild):
        role = guild.default_role
        for channel in guild.text_channels:
            await channel.set_permissions(role, send_messages=False)

    # Helper function to end the lockdown in the entire server
    async def _end_lockdown(self, guild: discord.Guild):
        role = guild.default_role
        for channel in guild.text_channels:
            await channel.set_permissions(role, send_messages=None)  # Reset to default permissions

    # Helper function to lockdown a specific channel
    async def _lockdown_channel(self, channel: discord.TextChannel):
        role = channel.guild.default_role
        await channel.set_permissions(role, send_messages=False)

    # Helper function to end lockdown in a specific channel
    async def _end_lockdown_channel(self, channel: discord.TextChannel):
        role = channel.guild.default_role
        await channel.set_permissions(role, send_messages=None)  # Reset to default permissions

async def setup(bot: commands.Bot):
    await bot.add_cog(ServerLockdown(bot))