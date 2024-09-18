import discord
from discord.ext import commands
from core import checks
from core.models import PermissionLevel
import datetime
from discord.utils import utcnow  # Ensure you import utcnow

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.logging_channel = None
        self.log_all = True  # Log all actions if True, or specific actions if False
        self.log_actions = set()  # Actions to log if log_all is False
        self.member_actions = {}  # To track actions taken on each member
        self.warning_id_counter = 0  # Counter for unique warning IDs

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
            self.log_actions.clear()  # Clear specific actions if logging all
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

    def has_higher_role(self, ctx: commands.Context, member: discord.Member) -> bool:
        """
        Check if the command author has a higher role than the member.
        """
        if ctx.author.guild_permissions.administrator:
            return True
        return ctx.author.top_role.position > member.top_role.position

    async def send_permission_error(self, ctx: commands.Context):
        """
        Send an error message if the user lacks permission to run the command on the specified member.
        """
        await ctx.send("❌ | You do not have permission to run this command on the specified member.")

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        """
        Ban a member from the server.
        """
        if member == ctx.author:
            await ctx.send("❌ | You cannot ban yourself.")
            return
        if not self.has_higher_role(ctx, member):
            return await self.send_permission_error(ctx)
        
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
        if member == ctx.author:
            await ctx.send("❌ | You cannot kick yourself.")
            return
        if not self.has_higher_role(ctx, member):
            return await self.send_permission_error(ctx)
        
        await member.kick(reason=reason)
        await ctx.send(f"👢 | {member.mention} has been kicked.")
        await self.log_action(ctx.guild, f"{member} was kicked for: {reason}")

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def timeout(self, ctx: commands.Context, member: discord.Member, duration: int, *, reason: str = None):
        """
        Timeout a member for a specific duration (in minutes).
        """
        if member == ctx.author:
            await ctx.send("❌ | You cannot timeout yourself.")
            return
        if not self.has_higher_role(ctx, member):
            return await self.send_permission_error(ctx)
        
        timeout_until = discord.utils.utcnow() + datetime.timedelta(minutes=duration)
        await member.edit(timeout_until=timeout_until, reason=reason)
        await ctx.send(f"⏲️ | {member.mention} has been timed out for {duration} minutes.")
        await self.log_action(ctx.guild, f"{member} was timed out for {duration} minutes for: {reason}")

        embed = discord.Embed(
            title="You Have Been Timed Out",
            description=f"**Reason:** {reason}\n**Timeout Until:** {timeout_until.isoformat()}",
            color=discord.Color.red()
        )
        embed.set_footer(text="AirAsia Group RBLX")
        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(f"⚠️ | Could not send a DM to {member.mention}.")

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def untimeout(self, ctx: commands.Context, member: discord.Member):
        """
        Remove a timeout from a member.
        """
        if member == ctx.author:
            await ctx.send("❌ | You cannot untimeout yourself.")
            return
        if not self.has_higher_role(ctx, member):
            return await self.send_permission_error(ctx)
        
        await member.edit(timeout_until=None)
        await ctx.send(f"✅ | {member.mention}'s timeout has been removed.")
        await self.log_action(ctx.guild, f"{member}'s timeout was removed.")

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        """
        Warn a member and send a warning ID.
        """
        if member == ctx.author:
            await ctx.send("❌ | You cannot warn yourself.")
            return
        if not self.has_higher_role(ctx, member):
            return await self.send_permission_error(ctx)
        
        self.warning_id_counter += 1
        warning_id = self.warning_id_counter

        if member.id not in self.member_actions:
            self.member_actions[member.id] = []
        self.member_actions[member.id].append((warning_id, reason))

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

        await ctx.send(f"⚠️ | {member.mention} has been warned for: {reason}\nWarning ID: {warning_id}")
        await self.log_action(ctx.guild, f"{member} was warned for: {reason} (ID: {warning_id})")

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def unwarn(self, ctx: commands.Context, member: discord.Member, warning_id: int):
        """
        Remove a warning from a member by its ID.
        """
        if member == ctx.author:
            await ctx.send("❌ | You cannot unwarn yourself.")
            return

        if not self.has_higher_role(ctx, member):
            return await self.send_permission_error(ctx)
        
        if member.id in self.member_actions:
            warnings = self.member_actions[member.id]
            new_warnings = [w for w in warnings if w[0] != warning_id]
            if len(new_warnings) == len(warnings):
                await ctx.send(f"❌ | No warning with ID {warning_id} found for {member.mention}.")
            else:
                self.member_actions[member.id] = new_warnings
                await ctx.send(f"⚠️ | Warning ID {warning_id} has been removed from {member.mention}.")
                await self.log_action(ctx.guild, f"Warning ID {warning_id} was removed from {member}.")
        else:
            await ctx.send(f"❌ | {member.mention} does not have any warnings.")

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def purge(self, ctx: commands.Context, amount: int):
        """
        Purge a large number of messages from the channel.
        """
        if amount <= 0 or amount > 100:
            await ctx.send("❌ | Please specify a number between 1 and 100.")
            return
        
        # Ensure the user has permission to purge messages
        if not ctx.channel.permissions_for(ctx.author).manage_messages:
            await ctx.send("❌ | You do not have permission to manage messages in this channel.")
            return
        
        await ctx.channel.purge(limit=amount)
        await ctx.send(f"🧹 | Purged {amount} messages.", delete_after=5)
        await self.log_action(ctx.guild, f"Purged {amount} messages in {ctx.channel}.")

    async def log_action(self, guild: discord.Guild, message: str):
        """
        Log an action if logging is enabled and the appropriate settings are in place.
        """
        if not self.logging_channel:
            return

        if self.log_all or message.split()[0].lower() in self.log_actions:
            await self.logging_channel.send(f"📝 | {message}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
