import openai
import discord
from discord.ext import commands

# Hardcoding the OpenAI API key (Not recommended for production)
openai.api_key = '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'

class ChatGPT(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.allowed_channel_id = 1315188226646085745  # Replace with the channel ID where ChatGPT is allowed

    @commands.command()
    async def chatgpt(self, ctx: commands.Context, *, prompt: str):
        """
        Command to interact with ChatGPT.
        This command will send a prompt to ChatGPT and return the response.
        Only available in a specific channel.
        """
        # Check if the command is used in the allowed channel
        if ctx.channel.id != self.allowed_channel_id:
            await ctx.send("❌ | This command can only be used in the designated channel.")
            return

        try:
            # Call OpenAI's GPT-3.5 model
            response = openai.Completion.create(
                model="gpt-3.5-turbo",  # Choose GPT-3.5
                prompt=prompt,
                max_tokens=150,  # Adjust token limit
                n=1,  # Number of responses to generate
                stop=None,  # Stop sequence (optional)
                temperature=0.7  # Control the randomness of the response
            )

            # Get the response from ChatGPT
            gpt_response = response.choices[0].text.strip()

            # Check if the response exceeds Discord's message limit
            if len(gpt_response) > 2000:
                await ctx.send("❌ | Error: The response exceeds the maximum Discord message length.")
            else:
                await ctx.send(gpt_response)

        except Exception as e:
            await ctx.send(f"❌ | An error occurred: {str(e)}")

async def setup(bot: commands.Bot):
    await bot.add_cog(ChatGPT(bot))
