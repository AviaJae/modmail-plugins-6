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
            # If no subcommand or name is provided, send the list of subcommands
            await ctx.send_help(ctx.command)

    @tag.command()
    async def list(self, ctx: commands.Context):
        """
        List all available tags
        """
        if self.tags:
            tag_list = "\n".join(f"- `{tag}`" for tag in self.tags.keys())
            embed = discord.Embed(
                title="Available Tags",
                description=tag_list,
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ | No tags available.")

    @tag.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
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
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
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
