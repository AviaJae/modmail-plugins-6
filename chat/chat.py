import discord
from discord.ext import commands
import openai

# Add your OpenAI API key here
openai.api_key = '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'

class ChatGPT(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Avoid the bot responding to itself
        if message.author == self.bot.user:
            return

        # Check if the message is in the specific channel (replace CHANNEL_ID with the actual channel ID)
        if message.channel.id != 1315188226646085745:
            return

        # Make the OpenAI API call for ChatGPT
        try:
            # Request to OpenAI's ChatGPT model
            response = openai.chat.Completion.create(
                model="gpt-3.5-turbo",  # Change model to gpt-4 for GPT-4
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message.content}
                ]
            )
            # Extract and send the response
            await message.channel.send(response['choices'][0]['message']['content'])

        except Exception as e:
            # Handle any errors that may occur
            await message.channel.send(f"❌ | An error occurred: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(ChatGPT(bot))
