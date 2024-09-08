import discord
from discord.ext import commands
import wavelink

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.music_queues = {}  # Dictionary to hold music queues for each voice channel
        self.current_players = {}  # Dictionary to track who is playing the music

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} has been loaded.")
        await self.connect_nodes()

    async def connect_nodes(self):
        """Connect to your Lavalink server."""
        try:
            node = await wavelink.NodePool.create_node(
                bot=self.bot,
                host='lava-v3.ajieblogs.eu.org',  # Lavalink host
                port=433,          # Lavalink port
                password='https://dsc.gg/ajidevserver',  # Lavalink password
                secure=True  # Set to True if using HTTPS
            )
            print(f"Connected to Lavalink node: {node.host}:{node.port}")
        except Exception as e:
            print(f"Failed to connect to Lavalink node: {e}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel and not before.channel:
            # Automatically join voice channel when a user joins
            if not self.bot.voice_clients:
                await after.channel.connect()
        elif before.channel and not after.channel:
            # Automatically disconnect from voice channel when no one is left
            if len(before.channel.members) == 1:
                await before.channel.guild.voice_client.disconnect()

    @commands.command()
    async def play(self, ctx, *, search: str):
        """Play music in a voice channel."""
        try:
            if not ctx.author.voice:
                return await ctx.send("You are not connected to a voice channel.")

            if not ctx.voice_client:
                await ctx.author.voice.channel.connect()

            vc = ctx.voice_client

            # Ensure a valid Lavalink node is connected
            if not wavelink.NodePool.nodes:
                return await ctx.send("No Lavalink nodes are currently connected.")

            # Search for the song
            tracks = await wavelink.YouTubeTrack.search(search, return_first=False)
            if not tracks:
                return await ctx.send("No tracks found.")

            track = tracks[0]  # Get the first track in the search results

            if ctx.voice_client.id not in self.music_queues:
                self.music_queues[ctx.voice_client.id] = []
                self.current_players[ctx.voice_client.id] = ctx.author

            self.music_queues[ctx.voice_client.id].append(track)

            if not vc.is_playing():
                await self.play_next(ctx)
            else:
                await ctx.send(f"Added to queue: {track.title}")

        except Exception as e:
            await ctx.send(f"An error occurred while trying to play: {e}")

    async def play_next(self, ctx):
        """Play the next track in the queue."""
        vc = ctx.voice_client

        if ctx.voice_client.id in self.music_queues and self.music_queues[ctx.voice_client.id]:
            track = self.music_queues[ctx.voice_client.id].pop(0)
            await vc.play(track)
            await ctx.send(f"Now playing: {track.title}")
        else:
            await ctx.send("Queue is empty.")

    @commands.command()
    async def pause(self, ctx):
        """Pause the currently playing track."""
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.send("No music is currently playing.")

        if self.current_players.get(vc.id) != ctx.author:
            return await ctx.send("You are not allowed to pause this music.")

        await vc.pause()
        await ctx.send("Playback paused.")

    @commands.command()
    async def resume(self, ctx):
        """Resume the currently paused track."""
        vc = ctx.voice_client
        if not vc or not vc.is_paused():
            return await ctx.send("No music is currently paused.")

        if self.current_players.get(vc.id) != ctx.author:
            return await ctx.send("You are not allowed to resume this music.")

        await vc.resume()
        await ctx.send("Playback resumed.")

    @commands.command()
    async def skip(self, ctx):
        """Skip the currently playing track."""
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.send("No music is currently playing.")

        if self.current_players.get(vc.id) != ctx.author:
            return await ctx.send("You are not allowed to skip this music.")

        vc.stop()
        await ctx.send("Skipped track.")
        await self.play_next(ctx)

    @commands.command()
    async def stop(self, ctx):
        """Stop the currently playing track."""
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.send("No music is currently playing.")

        if self.current_players.get(vc.id) != ctx.author:
            return await ctx.send("You are not allowed to stop this music.")

        vc.stop()
        self.music_queues.pop(vc.id, None)  # Clear the queue
        await ctx.send("Playback stopped.")

    @commands.command()
    async def leave(self, ctx):
        """Disconnect the bot from the voice channel."""
        vc = ctx.voice_client
        if not vc:
            return await ctx.send("I am not connected to a voice channel.")

        if vc.id in self.music_queues:
            self.music_queues.pop(vc.id, None)  # Clear the queue

        await vc.disconnect()
        await ctx.send("Disconnected from the voice channel.")

    @commands.command()
    async def queue(self, ctx):
        """Show the current queue."""
        vc = ctx.voice_client
        if not vc or not self.music_queues.get(vc.id):
            return await ctx.send("The queue is currently empty.")

        queue_list = [track.title for track in self.music_queues[vc.id]]
        await ctx.send(f"Current queue:\n" + "\n".join(queue_list))

    @commands.Cog.listener()
    async def on_wavelink_track_exception(self, player, track, error):
        """Handle track playback errors."""
        await player.ctx.send(f"An error occurred while playing: {error}")

async def setup(bot):
    await bot.add_cog(Music(bot))
