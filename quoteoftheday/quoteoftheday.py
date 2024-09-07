import discord
from discord.ext import commands
import requests
from datetime import datetime

class QuoteOfTheDaycommands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.quotes = {}  # Dictionary to store quotes

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def quoteofday(self, ctx: commands.Context):
        """
        Get the current quote of the day
        """
        if not self.quotes:
            await ctx.send("No quote of the day set.")
        else:
            today = datetime.utcnow().strftime("%Y-%m-%d")
            quote = self.quotes.get(today, "No quote of the day set.")
            await ctx.send(f"**Quote of the Day:**\n{quote}")

    @quoteofday.command(name='set')
    @commands.has_permissions(administrator=True)
    async def set_quote(self, ctx: commands.Context, *, quote: str):
        """
        Set the quote of the day
        """
        today = datetime.utcnow().strftime("%Y-%m-%d")
        self.quotes[today] = quote
        await ctx.send(f"✅ | Quote of the day has been set to:\n{quote}")

    @quoteofday.command(name='reset')
    @commands.has_permissions(administrator=True)
    async def reset_quote(self, ctx: commands.Context):
        """
        Reset the quote of the day
        """
        today = datetime.utcnow().strftime("%Y-%m-%d")
        if today in self.quotes:
            del self.quotes[today]
            await ctx.send("✅ | Quote of the day has been reset.")
        else:
            await ctx.send("No quote of the day set to reset.")

    @commands.command()
    async def getdailyquote(self, ctx: commands.Context):
        """
        Fetch and set a new daily quote from the They Said So Quotes API
        """
        url = "https://quotes.rest/qod?category=inspire"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            quote = data['contents']['quotes'][0]['quote']
            author = data['contents']['quotes'][0]['author']
            today = datetime.utcnow().strftime("%Y-%m-%d")
            self.quotes[today] = f"{quote} — {author}"
            await ctx.send(f"**Quote of the Day has been updated:**\n{self.quotes[today]}")
        else:
            await ctx.send("Failed to fetch a new quote. Please try again later.")

async def setup(bot: commands.Bot):
    await bot.add_cog(QuoteOfTheDay(bot))
