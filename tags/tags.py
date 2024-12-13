import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

import re

class Tags(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        # Dictionary to store tags
        self.tags = {}  # Format: {tag_name: {"message": str, "image_url": str}}

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def tag(self, ctx: commands.Context, name: str = None):
        """
        Retrieve or list tags
        """
        if name:
            # Retrieve the tag
            tag_data = self.tags.get(name)
            if tag_data:
                response = ""

    if "message" in tag_data and tag_data["message"]:
    response += tag_data["message"]

    if "image_url" in tag_data and tag_data["image_url"]:
    # Enclose the URL in < > to prevent embedding
    response += f"\n<{tag_data['image_url']}>"
               await ctx.send(response)
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
            await ctx.send(f"**Available Tags:**\n{tag_list}")
        else:
            await ctx.send("❌ | No tags available.")

    @tag.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def add(self, ctx: commands.Context, name: str, *, content: str):
        """
        Add a new tag with optional image URL.
        Usage: ?tag add <name> <message> [image_url]
        """
        if name in self.tags:
            await ctx.send(f"❌ | A tag with the name `{name}` already exists.")
            return

        # Extract message and optional image URL
        parts = content.split(" | ")
        message = parts[0].strip() if parts else None
        image_url = parts[1].strip() if len(parts) > 1 else None

        # Validate image URL if provided
        if image_url and not re.match(r"^(https?://[\\w\\-\\.]+\\.[a-z]{2,6}\\S*\\.(?:png|jpg|jpeg|gif|webp))$", image_url):
            await ctx.send("❌ | The provided image URL is invalid. Please provide a valid image URL (e.g., ending with .png, .jpg, etc.).")
            return

        self.tags[name] = {"message": message, "image_url": image_url}
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
