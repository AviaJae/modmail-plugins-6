import discord
from discord.ext import commands
import wavelink

class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        await self.bot.wait_until_ready()
        # Connect to Lavalink node
        await wavelink.NodePool.create_node(
            bot=self.bot,
            host='127.0.0.1',  # Lavalink host
            port=2333,         # Lavalink port
            password='youshallnotpass'  # Lavalink password
        )

    @commands.command(name='play')
    async def play(self, ctx, *, search: str):
        """Play a song or add it to the queue."""
        player = self.get_player(ctx)
        query = f'ytsearch:{search}'
        tracks = await wavelink.YouTubeTrack.search(query=query)
        
        if not tracks:
            return await ctx.send('No results found.')

        track = tracks[0]  # Play the first result

        # If not connected, connect to voice or stage channel
        if not player.is_connected():
            await self.connect_to_channel(ctx)
        
        await player.queue.put(track)
        await ctx.send(f'Added {track.title} to the queue.')

    async def connect_to_channel(self, ctx):
        """Connect to the author's voice or stage channel."""
        channel = ctx.author.voice.channel
        player = self.get_player(ctx)

        # Connect to voice or stage channel
        await channel.connect(cls=wavelink.Player)

        # If it's a stage channel, request to speak
        if isinstance(channel, discord.StageChannel):
            await ctx.guild.me.edit(suppress=False)  # Become a speaker
            await channel.guild.request_to_speak()  # Request to speak

    @commands.command(name='pause')
    async def pause(self, ctx):
        """Pause the currently playing track."""
        player = self.get_player(ctx)
        await player.pause()
        await ctx.send('Paused the music.')

    @commands.command(name='resume')
    async def resume(self, ctx):
        """Resume the currently paused track."""
        player = self.get_player(ctx)
        await player.resume()
        await ctx.send('Resumed the music.')

    @commands.command(name='skip')
    async def skip(self, ctx):
        """Skip the current track."""
        player = self.get_player(ctx)
        await player.stop()
        await ctx.send('Skipped the track.')

    @commands.command(name='queue')
    async def queue(self, ctx):
        """Show the current music queue."""
        player = self.get_player(ctx)
        if player.queue.is_empty:
            return await ctx.send('The queue is empty.')
        
        queue = '\n'.join([track.title for track in player.queue._queue])
        await ctx.send(f'Queue:\n{queue}')

    @commands.command(name='playlist')
    async def playlist(self, ctx, playlist_name: str):
        """Play a playlist from YouTube."""
        player = self.get_player(ctx)
        query = f'ytsearch:{playlist_name} playlist'
        tracks = await wavelink.YouTubeTrack.search(query=query)

        if not tracks:
            return await ctx.send('No playlist found.')

        if not player.is_connected():
            await self.connect_to_channel(ctx)

        for track in tracks:
            await player.queue.put(track)
        
        await ctx.send(f'Added playlist {playlist_name} to the queue.')

    def get_player(self, ctx):
        """Gets the current player."""
        return self.bot.wavelink.get_player(ctx.guild.id, cls=wavelink.Player)

async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))
