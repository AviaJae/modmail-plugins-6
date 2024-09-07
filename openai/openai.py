import discord
from discord.ext import commands
import openai
import os

class ChatBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.configured_channels = [1281998280901005442, 1281998366276059299]  # Replace with your channel IDs
        self.api_key = None

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setapikey(self, ctx: commands.Context, api_key: str):
        """
        Set the OpenAI API key. Only available to administrators.
        """
        self.api_key = api_key
        openai.api_key = self.api_key
        await ctx.send("OpenAI API key has been set successfully.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def getapikey(self, ctx: commands.Context):
        """
        Retrieve the currently set OpenAI API key. Only available to administrators.
        """
        if self.api_key:
            await ctx.send(f"Current API key: {self.api_key}")
        else:
            await ctx.send("No API key is set.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Avoid the bot responding to itself and messages outside the configured channels
        if message.author == self.bot.user or message.channel.id not in self.configured_channels:
            return

        if not self.api_key:
            await message.channel.send("API key is not set. Please use the `!setapikey` command to set it.")
            return

        try:
            # Call the ChatGPT API
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=message.content,
                max_tokens=150
            )

            # Send the response back to the Discord channel
            await message.channel.send(response.choices[0].text.strip())

        except Exception as e:
            # Handle errors (e.g., API errors)
            await message.channel.send(f"An error occurred: {e}")

def setup(bot):
    bot.add_cog(ChatBot(bot))
