import discord
from discord.ext import commands
import openai

# Define your OpenAI API key
openai.api_key = "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"

class ChatGPT(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Automatically prompts ChatGPT on a message sent in a specific channel"""
        # Avoid the bot replying to itself
        if message.author == self.bot.user:
            return

        # Define the specific channel ID where the ChatGPT feature can be used
        SPECIFIC_CHANNEL_ID = 1315188226646085745  # Replace with your specific channel ID

        # Ensure the message is sent in the correct channel
        if message.channel.id != SPECIFIC_CHANNEL_ID:
            return  # Don't do anything if it's not the specific channel

        # Send the request to OpenAI's API
        try:
            # Use the newer chat API interface
            response = openai.chat_completions.create(
                model="gpt-3.5-turbo",  # Use GPT-3.5 model
                messages=[{"role": "user", "content": message.content}],
                max_tokens=150,  # Limit the number of tokens to control the response length
                temperature=0.7  # Adjust for response creativity (0.0 - 1.0)
            )

            # Get the response text
            answer = response['choices'][0]['message']['content'].strip()

            # Handle long responses that exceed Discord's 2000 character limit
            if len(answer) > 2000:
                for i in range(0, len(answer), 2000):
                    await message.channel.send(answer[i:i + 2000])
            else:
                await message.channel.send(answer)

        except Exception as e:
            await message.channel.send(f"Error: {e}")  # Send an error message if something goes wrong

# Add the cog to the bot
async def setup(bot: commands.Bot):
    await bot.add_cog(ChatGPT(bot))
