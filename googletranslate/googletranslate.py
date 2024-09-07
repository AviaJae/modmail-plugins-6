import discord
from discord.ext import commands
from translate import Translator

class Translate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator(to_lang="en")  # Default target language

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} has been loaded.")

    @commands.command(name='setlang')
    @commands.has_permissions(administrator=True)
    async def set_language(self, ctx, lang_code: str):
        """Sets the target language for translations."""
        self.translator = Translator(to_lang=lang_code)
        await ctx.send(f"Target language set to {lang_code}.")

    @commands.command(name='translate')
    async def translate_text(self, ctx, *, text: str):
        """Translates the provided text to the target language."""
        try:
            translation = self.translator.translate(text)
            await ctx.send(f"Translated text: {translation}")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(Translate(bot))
