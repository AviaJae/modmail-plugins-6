import discord
from discord.ext import commands
import wavelink

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} has been loaded.")
        # Connect the node when the bot is ready
        await self.connect_nodes()

    async def connect_nodes(self):
        """Connect to Lavalink server nodes."""
        try:
            await wavelink.NodePool.create_node(
                bot=self.bot,
                host='lavalink-legacy.jompo.cloud',  # Lavalink host
                port=2333,          # Lavalink port
                password='jompo'  # Lavalink password
            )
            print("Successfully connected to Lavalink node.")
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

    @commands.command()
    async def stage(self, ctx):
        """Move the bot to a stage channel."""
        try:
            if not ctx.author.voice or ctx.author.voice.channel.type != discord.ChannelType.stage_voice:
                return await ctx.send("You need to be in a stage channel to use this command.")

            channel = ctx.author.voice.channel
            if not ctx.voice_client:
                await channel.connect(cls=wavelink.Player)

            # Set the bot as a stage speaker
            await ctx.guild.me.edit(suppress=False)
            await ctx.send(f"Connected to stage: {channel.name}.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player, track, reason):
        """Automatically disconnect after the track ends."""
        if reason == 'FINISHED':
            await player.disconnect()

    @commands.Cog.listener()
    async def on_wavelink_track_exception(self, player, track, error):
        """Handle track playback errors."""
        await player.ctx.send(f"An error occurred while playing: {error}")


async def setup(bot):
    await bot.add_cog(Music(bot))
