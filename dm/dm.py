import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

class DMPlugin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def dm(self, ctx: commands.Context):
        """
        Send a DM to a user
        """
        await ctx.send_help(ctx.command)

    @dm.command()
    async def send(self, ctx: commands.Context, user: discord.User, *, message: str):
        """
        Send a direct message to a user
        """
        try:
            await user.send(message)
            await ctx.send(f"✅ | Message sent to {user.mention}.")
        except discord.Forbidden:
            await ctx.send(f"❌ | I do not have permission to send a message to {user.mention}.")
        except discord.HTTPException:
            await ctx.send(f"❌ | An error occurred while trying to send the message to {user.mention}.")

async def setup(bot: commands.Bot):
    await bot.add_cog(DM(bot))
