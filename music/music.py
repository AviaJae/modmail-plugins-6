import discord
from discord.ext import commands
import wavelink

class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        await self.bot.wait_until_ready()
        try:
            # Connect to Lavalink node
            await wavelink.NodePool.create_node(
                bot=self.bot,
                host='lavalink.jompo.cloud',  # Lavalink host
                port=2333,         # Lavalink port
                password='jompo'  # Lavalink password
            )
        except Exception as e:
            print(f"Failed to connect to Lavalink node: {e}")

    @commands.command(name='play')
    async def play(self, ctx, *, search: str):
        """Play a song or add it to the queue."""
        try:
            player = self.get_player(ctx)
            query = f'ytsearch:{search}'
            tracks = await wavelink.YouTubeTrack.search(query=query)

            if not tracks:
                return await ctx.send('No results found for your search.')

            track = tracks[0]  # Play the first result

            # If not connected, connect to voice or stage channel
            if not player.is_connected():
                await self.connect_to_channel(ctx)

            await player.queue.put(track)
            await ctx.send(f'Added {track.title} to the queue.')
        
        except Exception as e:
            await ctx.send(f"An error occurred while playing: {e}")

    async def connect_to_channel(self, ctx):
        """Connect to the author's voice or stage channel."""
        try:
            channel = ctx.author.voice.channel
            player = self.get_player(ctx)

            # Connect to voice or stage channel
            await channel.connect(cls=wavelink.Player)

            # If it's a stage channel, request to speak
            if isinstance(channel, discord.StageChannel):
                await ctx.guild.me.edit(suppress=False)  # Become a speaker
                await channel.guild.request_to_speak()  # Request to speak
        
        except AttributeError:
            await ctx.send("You're not connected to a voice channel.")
        except Exception as e:
            await ctx.send(f"Failed to connect to channel: {e}")

    @commands.command(name='pause')
    async def pause(self, ctx):
        """Pause the currently playing track."""
        try:
            player = self.get_player(ctx)
            await player.pause()
            await ctx.send('Paused the music.')
        
        except Exception as e:
            await ctx.send(f"An error occurred while pausing: {e}")

    @commands.command(name='resume')
    async def resume(self, ctx):
        """Resume the currently paused track."""
        try:
            player = self.get_player(ctx)
            await player.resume()
            await ctx.send('Resumed the music.')
        
        except Exception as e:
            await ctx.send(f"An error occurred while resuming: {e}")

    @commands.command(name='skip')
    async def skip(self, ctx):
        """Skip the current track."""
        try:
            player = self.get_player(ctx)
            await player.stop()
            await ctx.send('Skipped the track.')
        
        except Exception as e:
            await ctx.send(f"An error occurred while skipping: {e}")

    @commands.command(name='queue')
    async def queue(self, ctx):
        """Show the current music queue."""
        try:
            player = self.get_player(ctx)
            if player.queue.is_empty:
                return await ctx.send('The queue is empty.')

            queue = '\n'.join([track.title for track in player.queue._queue])
            await ctx.send(f'Queue:\n{queue}')
        
        except Exception as e:
            await ctx.send(f"An error occurred while fetching the queue: {e}")

    @commands.command(name='playlist')
    async def playlist(self, ctx, playlist_name: str):
        """Play a playlist from YouTube."""
        try:
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
        
        except Exception as e:
            await ctx.send(f"An error occurred while adding the playlist: {e}")

    def get_player(self, ctx):
        """Gets the current player or creates one."""
        return self.bot.wavelink.get_player(ctx.guild.id, cls=wavelink.Player)

async def setup(bot):
    try:
        await bot.add_cog(MusicPlayer(bot))
        print("Music Player cog loaded successfully.")
    except Exception as e:
        print(f"Failed to load Music Player cog: {e}")
