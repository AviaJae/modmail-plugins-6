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
    async def start(self, ctx: commands.Context):
        """
        Start the lockdown - prevents all members from sending messages in all channels.
        """
        await self._lockdown(ctx.guild)
        await ctx.send("🔒 | The server has been locked down. Members cannot send messages.")

    @lockdown.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def end(self, ctx: commands.Context):
        """
        End the lockdown - restores message permissions to all channels.
        """
        await self._end_lockdown(ctx.guild)
        await ctx.send("🔓 | The server lockdown has been lifted. Members can send messages again.")

    @lockdown.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def schedule_start(self, ctx: commands.Context, time: str):
        """
        Schedule a lockdown to start at a specific time (format: HH:MM 24-hour format).
        """
        try:
            lockdown_time = datetime.strptime(time, "%H:%M").time()
            now = datetime.now().time()

            # Calculate the time difference and schedule the task
            if lockdown_time > now:
                time_delta = datetime.combine(datetime.today(), lockdown_time) - datetime.combine(datetime.today(), now)
            else:
                time_delta = datetime.combine(datetime.today() + timedelta(days=1), lockdown_time) - datetime.combine(datetime.today(), now)

            await ctx.send(f"⏰ | Lockdown scheduled to start at {lockdown_time} (in {time_delta}).")
            await asyncio.sleep(time_delta.total_seconds())
            await self._lockdown(ctx.guild)
            await ctx.send("🔒 | The server has been locked down.")
        
        except ValueError:
            await ctx.send("❌ | Invalid time format. Please use HH:MM (24-hour format).")

    @lockdown.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def schedule_end(self, ctx: commands.Context, time: str):
        """
        Schedule a lockdown to end at a specific time (format: HH:MM 24-hour format).
        """
        try:
            end_time = datetime.strptime(time, "%H:%M").time()
            now = datetime.now().time()

            # Calculate the time difference and schedule the task
            if end_time > now:
                time_delta = datetime.combine(datetime.today(), end_time) - datetime.combine(datetime.today(), now)
            else:
                time_delta = datetime.combine(datetime.today() + timedelta(days=1), end_time) - datetime.combine(datetime.today(), now)

            await ctx.send(f"⏰ | Lockdown scheduled to end at {end_time} (in {time_delta}).")
            await asyncio.sleep(time_delta.total_seconds())
            await self._end_lockdown(ctx.guild)
            await ctx.send("🔓 | The server lockdown has been lifted.")
        
        except ValueError:
            await ctx.send("❌ | Invalid time format. Please use HH:MM (24-hour format).")

    @lockdown.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def schedule_both(self, ctx: commands.Context, start_time: str, end_time: str):
        """
        Schedule both a lockdown start and end (start: HH:MM, end: HH:MM).
        """
        try:
            start_lockdown_time = datetime.strptime(start_time, "%H:%M").time()
            end_lockdown_time = datetime.strptime(end_time, "%H:%M").time()
            now = datetime.now().time()

            # Calculate the time differences for start and end
            if start_lockdown_time > now:
                start_delta = datetime.combine(datetime.today(), start_lockdown_time) - datetime.combine(datetime.today(), now)
            else:
                start_delta = datetime.combine(datetime.today() + timedelta(days=1), start_lockdown_time) - datetime.combine(datetime.today(), now)

            if end_lockdown_time > now:
                end_delta = datetime.combine(datetime.today(), end_lockdown_time) - datetime.combine(datetime.today(), now)
            else:
                end_delta = datetime.combine(datetime.today() + timedelta(days=1), end_lockdown_time) - datetime.combine(datetime.today(), now)

            # Schedule lockdown start
            await ctx.send(f"⏰ | Lockdown scheduled to start at {start_lockdown_time}.")
            await asyncio.sleep(start_delta.total_seconds())
            await self._lockdown(ctx.guild)
            await ctx.send("🔒 | The server has been locked down.")

            # Schedule lockdown end
            await ctx.send(f"⏰ | Lockdown scheduled to end at {end_lockdown_time}.")
            await asyncio.sleep(end_delta.total_seconds())
            await self._end_lockdown(ctx.guild)
            await ctx.send("🔓 | The server lockdown has been lifted.")
        
        except ValueError:
            await ctx.send("❌ | Invalid time format. Please use HH:MM (24-hour format).")

    # Helper function to lockdown the server (prevent @everyone from sending messages)
    async def _lockdown(self, guild: discord.Guild):
        role = guild.default_role
        for channel in guild.text_channels:
            await channel.set_permissions(role, send_messages=False)

    # Helper function to end the lockdown (allow @everyone to send messages)
    async def _end_lockdown(self, guild: discord.Guild):
        role = guild.default_role
        for channel in guild.text_channels:
            await channel.set_permissions(role, send_messages=None)  # Reset to default permissions

async def setup(bot: commands.Bot):
    await bot.add_cog(ServerLockdown(bot))