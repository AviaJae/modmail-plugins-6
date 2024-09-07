import discord
from discord.ext import commands
from googletrans import Translator, LANGUAGES

class Translate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator()

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
        if lang not in LANGUAGES:
            await ctx.send(f":x: | `{lang}` is not a valid language code. Use a valid language code like 'en', 'es', 'fr', etc.")
            return
        
        try:
            translated = self.translator.translate(text, dest=lang)
            await ctx.send(f"**Original Text:** {text}\n**Translated Text:** {translated.text}")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

def setup(bot):
    bot.add_cog(Translate(bot))
