import discord
from discord.ext import commands
from core import checks
from core.models import PermissionLevel
import datetime

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.logging_channel = None
        self.log_all = True  # If true, logs all actions, otherwise logs specific actions
        self.log_actions = set()  # Contains specific actions to log if `log_all` is False
        self.member_actions = {}  # Dictionary to track actions for each member
        self.warning_id_counter = 0  # Counter to generate unique warning IDs
        self.warnings = {}  # Dictionary to track warnings with their IDs

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def modlog(self, ctx: commands.Context):
        """
        Manage moderation logging settings.
        """
        await ctx.send_help(ctx.command)

    @modlog.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def setchannel(self, ctx: commands.Context, channel: discord.TextChannel):
        """
        Set the channel for logging moderation actions.
        """
        self.logging_channel = channel
        await ctx.send(f"✅ | Logging channel set to {channel.mention}.")

    @modlog.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def setlogmode(self, ctx: commands.Context, mode: str):
        """
        Set logging mode to either 'all' or 'specific' (only certain actions).
        """
        if mode.lower() == 'all':
            self.log_all = True
            self.log_actions.clear()  # Clear any specific actions
            await ctx.send("✅ | Logging set to all actions.")
        elif mode.lower() == 'specific':
            self.log_all = False
            await ctx.send("✅ | Logging set to specific actions. Use `modlog addaction` to specify actions.")
        else:
            await ctx.send("❌ | Invalid mode. Use either 'all' or 'specific'.")

    @modlog.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def addaction(self, ctx: commands.Context, action: str):
        """
        Add a specific action to log (ban, unban, kick, timeout, warn, unwarn, purge).
        """
        valid_actions = {'ban', 'unban', 'kick', 'timeout', 'warn', 'unwarn', 'purge'}
        if action.lower() in valid_actions:
            self.log_actions.add(action.lower())
            await ctx.send(f"✅ | Action `{action}` added to log.")
        else:
            await ctx.send(f"❌ | Invalid action. Valid actions are: {', '.join(valid_actions)}")

    @modlog.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def removeaction(self, ctx: commands.Context, action: str):
        """
        Remove a specific action from logging.
        """
        if action.lower() in self.log_actions:
            self.log_actions.remove(action.lower())
            await ctx.send(f"✅ | Action `{action}` removed from logging.")
        else:
            await ctx.send("❌ | That action isn't being logged.")

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        """
        Ban a member from the server.
        """
        await member.ban(reason=reason)
        await ctx.send(f"🔨 | {member.mention} has been banned.")
        await self.log_action(ctx.guild, f"{member} was banned for: {reason}")

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def unban(self, ctx: commands.Context, user: discord.User):
        """
        Unban a user from the server.
        """
        await ctx.guild.unban(user)
        await ctx.send(f"✅ | {user.mention} has been unbanned.")
        await self.log_action(ctx.guild, f"{user} was unbanned.")

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        """
        Kick a member from the server.
        """
        await member.kick(reason=reason)
        await ctx.send(f"👢 | {member.mention} has been kicked.")
        await self.log_action(ctx.guild, f"{member} was kicked for: {reason}")

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def timeout(self, ctx: commands.Context, member: discord.Member, duration: int, *, reason: str = None):
        """
        Timeout a member for a specific duration (in minutes).
        """
        timeout_until = datetime.datetime.utcnow() + datetime.timedelta(minutes=duration)
        await member.timeout(until=timeout_until, reason=reason)
        await ctx.send(f"⏲️ | {member.mention} has been timed out for {duration} minutes.")
        await self.log_action(ctx.guild, f"{member} was timed out for {duration} minutes for: {reason}")

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        """
        Warn a member and send an embed message in their DM.
        """
        self.warning_id_counter += 1
        warning_id = self.warning_id_counter

        # Track the warning
        if member.id not in self.member_actions:
            self.member_actions[member.id] = []
        self.member_actions[member.id].append((warning_id, reason))

        # Send DM with warning details
        embed = discord.Embed(
            title="You Have Been Warned",
            description=f"**Reason:** {reason}\n**Warning ID:** {warning_id}",
            color=discord.Color.red()
        )
        embed.set_footer(text="AirAsia Group RBLX")
        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(f"⚠️ | Could not send a DM to {member.mention}.")

        # Log the warning in the channel
        await ctx.send(f"⚠️ | {member.mention} has been warned for: {reason}\nWarning ID: {warning_id}")
        await self.log_action(ctx.guild, f"{member} was warned for: {reason} (ID: {warning_id})")

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def unwarn(self, ctx: commands.Context, member: discord.Member, warning_id: int):
        """
        Remove a warning from a member based on its ID.
        """
        if member.id in self.member_actions:
            warnings = self.member_actions[member.id]
            self.member_actions[member.id] = [w for w in warnings if w[0] != warning_id]

            # Inform user
            await ctx.send(f"⚠️ | Warning ID {warning_id} has been removed from {member.mention}.")
            await self.log_action(ctx.guild, f"Warning ID {warning_id} was removed from {member}.")

        else:
            await ctx.send(f"❌ | {member.mention} does not have any warnings.")

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def checkwarnings(self, ctx: commands.Context, member: discord.Member):
        """
        Check the warnings for a member.
        """
        if member.id in self.member_actions:
            warnings = self.member_actions[member.id]
            if warnings:
                response = "\n".join([f"ID: {w[0]}, Reason: {w[1]}" for w in warnings])
            else:
                response = "No warnings found."
        else:
            response = "No warnings found."

        await ctx.send(f"Warnings for {member.mention}:\n{response}")

    async def log_action(self, guild: discord.Guild, message: str):
        """
        Log an action if logging is enabled and the appropriate settings are in place.
        """
        if not self.logging_channel:
            return  # No logging channel set

        if self.log_all or message.split()[0].lower() in self.log_actions:
            await self.logging_channel.send(f"📝 | {message}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))