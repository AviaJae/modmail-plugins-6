import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

class DirectMessages(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        # Store DM message IDs in memory
        self.sent_dms = {}  # Format: {user_id: message_id}

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def dm(self, ctx: commands.Context):
        """
        Send a DM to a user
        """
        await ctx.send_help(ctx.command)

    @dm.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def send(self, ctx: commands.Context, user: discord.User, *, message: str):
        """
        Send a direct message to a user.
        """
        try:
            sent_message = await user.send(message)
            # Store the DM ID
            self.sent_dms[user.id] = sent_message.id
            await ctx.send(f"✅ | Message sent to {user.mention}. DM ID: `{sent_message.id}`")
        except discord.Forbidden:
            await ctx.send(f"❌ | I do not have permission to send a message to {user.mention}.")
        except discord.HTTPException:
            await ctx.send(f"❌ | An error occurred while trying to send the message to {user.mention}.")

    @dm.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def delete(self, ctx: commands.Context, user: discord.User):
        """
        Delete the most recent DM sent to a user by the bot
        """
        try:
            message_id = self.sent_dms.get(user.id)
            if not message_id:
                await ctx.send(f"❌ | No record of a DM to {user.mention} found.")
                return

            channel = user.dm_channel or await user.create_dm()
            message = await channel.fetch_message(message_id)
            await message.delete()
            del self.sent_dms[user.id]
            await ctx.send(f"✅ | Deleted the DM sent to {user.mention}.")
        except discord.Forbidden:
            await ctx.send(f"❌ | I do not have permission to delete the message for {user.mention}.")
        except discord.HTTPException:
            await ctx.send(f"❌ | An error occurred while trying to delete the message for {user.mention}.")
        except discord.NotFound:
            await ctx.send(f"❌ | The DM to {user.mention} could not be found (possibly deleted already).")

async def setup(bot: commands.Bot):
    await bot.add_cog(DirectMessages(bot))
