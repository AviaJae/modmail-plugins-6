import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

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
                embed = discord.Embed(color=discord.Color.blue())

                if "message" in tag_data and tag_data["message"]:
                    embed.description = tag_data["message"]

                if "image_url" in tag_data and tag_data["image_url"]:
                    embed.set_image(url=tag_data["image_url"])

                await ctx.send(embed=embed)
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
