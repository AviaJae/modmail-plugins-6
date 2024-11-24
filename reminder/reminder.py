import discord
from discord.ext import commands, tasks
from core import checks
from core.models import PermissionLevel
import asyncio
import uuid
from datetime import datetime, timedelta

class Reminder(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.reminders = {}  # Format: {reminder_id: {user_id, target_id, message, time}}

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def remind(self, ctx: commands.Context):
        """
        Reminder commands
        """
        await ctx.send_help(ctx.command)

    @remind.command()
    async def create(self, ctx: commands.Context, member: discord.Member, time: str, *, message: str):
        """
        Create a reminder for yourself or another member.
        Time format: <number><s|m|h|d> (e.g., 10s, 5m, 2h, 1d)
        """
        # Convert time to seconds
        time_delta = self.parse_time(time)
        if time_delta is None:
            await ctx.send("❌ | Invalid time format. Use <number><s|m|h|d> (e.g., 10s, 5m, 2h, 1d).")
            return

        reminder_time = datetime.utcnow() + time_delta
        reminder_id = str(uuid.uuid4())[:16]  # Generate a unique 16-char ID

        self.reminders[reminder_id] = {
            "user_id": ctx.author.id,
            "target_id": member.id,
            "message": message,
            "time": reminder_time,
        }

        await ctx.send(f"✅ | Reminder created for {member.mention} with ID `{reminder_id}`. You will be reminded in {time}.")

        # Schedule the reminder
        self.bot.loop.create_task(self.send_reminder(reminder_id))

    @remind.command()
    async def delete(self, ctx: commands.Context, reminder_id: str):
        """
        Delete a self-created reminder using its ID.
        """
        reminder = self.reminders.get(reminder_id)

        if not reminder:
            await ctx.send(f"❌ | Reminder with ID `{reminder_id}` not found.")
            return

        if reminder["user_id"] != ctx.author.id:
            await ctx.send("❌ | You can only delete reminders you created.")
            return

        del self.reminders[reminder_id]
        await ctx.send(f"✅ | Reminder with ID `{reminder_id}` has been deleted.")

    def parse_time(self, time_str: str):
        """Helper function to parse time strings into timedelta."""
        try:
            unit = time_str[-1].lower()
            value = int(time_str[:-1])
            if unit == "s":
                return timedelta(seconds=value)
            elif unit == "m":
                return timedelta(minutes=value)
            elif unit == "h":
                return timedelta(hours=value)
            elif unit == "d":
                return timedelta(days=value)
        except (ValueError, IndexError):
            return None

    async def send_reminder(self, reminder_id: str):
        """Handles sending reminders after the specified time."""
        reminder = self.reminders.get(reminder_id)
        if not reminder:
            return

        time_to_wait = (reminder["time"] - datetime.utcnow()).total_seconds()
        if time_to_wait > 0:
            await asyncio.sleep(time_to_wait)

        reminder = self.reminders.pop(reminder_id, None)  # Remove the reminder after sending
        if reminder:
            target = self.bot.get_user(reminder["target_id"])
            if target:
                try:
                    await target.send(f"⏰ | Reminder: {reminder['message']}")
                except discord.Forbidden:
                    pass

            creator = self.bot.get_user(reminder["user_id"])
            if creator:
                try:
                    await creator.send(f"⏰ | Reminder for {target.mention} has been sent: {reminder['message']}")
                except discord.Forbidden:
                    pass

async def setup(bot: commands.Bot):
    await bot.add_cog(Reminder(bot))
