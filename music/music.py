import discord
from discord.ext import commands
import aiohttp

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} has been loaded.")

    @commands.command()
    async def join(self, ctx):
        """Join a voice channel."""
        try:
            if not ctx.author.voice:
                return await ctx.send("You are not connected to a voice channel.")
            
            channel = ctx.author.voice.channel
            if ctx.voice_client:
                return await ctx.voice_client.move_to(channel)
            
            await channel.connect()
            await ctx.send(f"Joined {channel.name}.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.command()
    async def play(self, ctx, url: str):
        """Play audio from a URL in the voice channel."""
        if not ctx.voice_client:
            return await ctx.send("I need to be in a voice channel to play audio.")

        vc = ctx.voice_client
        if not vc.is_playing():
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await ctx.send("Failed to fetch audio.")
                    
                    audio_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(resp.url))
                    vc.play(audio_source)
                    await ctx.send(f"Now playing: {url}")
        else:
            await ctx.send("Already playing audio.")

    @commands.command()
    async def stop(self, ctx):
        """Stop the currently playing track."""
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.send("No music is currently playing.")

        vc.stop()
        await ctx.send("Playback stopped.")

    @commands.command()
    async def pause(self, ctx):
        """Pause the currently playing track."""
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.send("No music is currently playing.")

        vc.pause()
        await ctx.send("Playback paused.")

    @commands.command()
    async def resume(self, ctx):
        """Resume the currently paused track."""
        vc = ctx.voice_client
        if not vc or vc.is_playing():
            return await ctx.send("No music is paused.")

        vc.resume()
        await ctx.send("Playback resumed.")

    @commands.command()
    async def leave(self, ctx):
        """Disconnect the bot from the voice channel."""
        vc = ctx.voice_client
        if not vc:
            return await ctx.send("I am not connected to a voice channel.")

        await vc.disconnect()
        await ctx.send("Disconnected from the voice channel.")

async def setup(bot):
    await bot.add_cog(Music(bot))
