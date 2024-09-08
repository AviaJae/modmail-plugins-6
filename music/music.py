import discord
from discord.ext import commands
import wavelink

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} has been loaded.")
        # Attempt to connect the Lavalink node when the bot is ready
        await self.connect_nodes()

    async def connect_nodes(self):
        """Connect to the Lavalink server nodes."""
        try:
            # Connect to your Lavalink server
            node = await wavelink.NodePool.create_node(
                bot=self.bot,
                host='lavalink-legacy.jompo.cloud',  # Lavalink host
                port=2333,          # Lavalink port
                password='jompo'  # Lavalink password
            )
            print(f"Connected to Lavalink node: {node.host}:{node.port}")
        except Exception as e:
            print(f"Failed to connect to Lavalink node: {e}")

    @commands.command()
    async def join(self, ctx):
        """Join a voice channel."""
        try:
            if not ctx.author.voice:
                return await ctx.send("You are not connected to a voice channel.")
            
            channel = ctx.author.voice.channel
            if ctx.voice_client:
                return await ctx.voice_client.move_to(channel)
            
            await channel.connect(cls=wavelink.Player)
            await ctx.send(f"Joined {channel.name}.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.command()
    async def play(self, ctx, *, search: str):
        """Play music in a voice channel."""
        try:
            if not ctx.voice_client:
                await self.join(ctx)  # Join the voice channel if not already in one

            vc = ctx.voice_client
            if not vc:
                return await ctx.send("I am not connected to a voice channel.")

            if not wavelink.NodePool.nodes:
                return await ctx.send("No nodes are currently connected.")

            # Search for the song
            track = await wavelink.YouTubeTrack.search(search, return_first=True)
            if not track:
                return await ctx.send("No tracks found.")

            if not vc.is_playing():
                await vc.play(track)
                await ctx.send(f"Now playing: {track.title}")
            else:
                await ctx.send(f"Currently playing: {vc.source.title}")
        except Exception as e:
            await ctx.send(f"An error occurred while trying to play: {e}")

    @commands.command()
    async def stop(self, ctx):
        """Stop the currently playing track."""
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.send("No music is currently playing.")

        await vc.stop()
        await ctx.send("Playback stopped.")

    @commands.command()
    async def pause(self, ctx):
        """Pause the currently playing track."""
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.send("No music is currently playing.")

        await vc.pause()
        await ctx.send("Playback paused.")

    @commands.command()
    async def resume(self, ctx):
        """Resume the currently paused track."""
        vc = ctx.voice_client
        if not vc or vc.is_playing():
            return await ctx.send("No music is paused.")

        await vc.resume()
        await ctx.send("Playback resumed.")

    @commands.command()
    async def leave(self, ctx):
        """Disconnect the bot from the voice channel."""
        vc = ctx.voice_client
        if not vc:
            return await ctx.send("I am not connected to a voice channel.")

        await vc.disconnect()
        await ctx.send("Disconnected from the voice channel.")

    @commands.Cog.listener()
    async def on_wavelink_track_exception(self, player, track, error):
        """Handle track playback errors."""
        await player.ctx.send(f"An error occurred while playing: {error}")


async def setup(bot):
    await bot.add_cog(Music(bot))
