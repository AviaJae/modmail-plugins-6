import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

class Tags(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        # Dictionary to store tags
        self.tags = {}  # Format: {tag_name: tag_message}

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def tag(self, ctx: commands.Context, name: str = None):
        """
        Retrieve or list tags
        """
        if name:
            # Retrieve the tag
            tag_message = self.tags.get(name)
            if tag_message:
                await ctx.send(tag_message)
            else:
                await ctx.send(f"❌ | Tag `{name}` not found.")
        else:
            # List all available tags
            if self.tags:
                tag_list = ", ".join(self.tags.keys())
                await ctx.send(f"Available tags: {tag_list}")
            else:
                await ctx.send("No tags available.")

    @tag.command()
    @checks.has_permissions(PermissionLevel.SUPPORTER)
    async def add(self, ctx: commands.Context, name: str, *, message: str):
        """
        Add a new tag
        """
        if name in self.tags:
            await ctx.send(f"❌ | A tag with the name `{name}` already exists.")
            return

        self.tags[name] = message
        await ctx.send(f"✅ | Tag `{name}` added successfully!")

    @tag.command()
    @checks.has_permissions(PermissionLevel.SUPPORTER)
    async def delete(self, ctx: commands.Context, name: str):
        """
        Delete a tag
        """
        if name not in self.tags:
            await ctx.send(f"❌ | Tag `{name}` does not exist.")
            return

        del self.tags[name]
        await ctx.send(f"✅ | Tag `{name}` deleted successfully!")

async def setup(bot: commands.Bot):
    await bot.add_cog(Tags(bot))
