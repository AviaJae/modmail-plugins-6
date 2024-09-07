import discord
from discord.ext import commands
from translate import Translator

class TranslatePlugin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def translate(self, ctx):
        """
        Translate text into a specified language.
        Usage: !translate <language_code> <text>
        Example: !translate es Hello world
        """
        await ctx.send_help(ctx.command)

    @translate.command()
    async def text(self, ctx, lang: str, *, text: str):
        """
        Translate a given text into the specified language.
        """
        try:
            translator = Translator(to_lang=lang)
            translated = translator.translate(text)
            await ctx.send(f"**Original Text:** {text}\n**Translated Text:** {translated}")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

def setup(bot):
    bot.add_cog(TranslatePlugin(bot))
