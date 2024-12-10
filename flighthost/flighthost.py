import discord
from discord.ext import commands
import uuid
import time
import re
import pytz
import parsedatetime

from core import checks
from core.models import PermissionLevel


class FlightHosting(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.flights = {}
        self.cal = parsedatetime.Calendar()
        self.timezone = pytz.timezone("Asia/Kuala_Lumpur")

    @staticmethod
    def parse_location(location: str) -> str:
        """
        Extracts text within parentheses. E.g., '(Penang)' -> 'Penang'
        """
        match = re.match(r"\((.*?)\)", location)
        return match.group(1) if match else None

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def createflight(
        self,
        ctx,
        channel: discord.TextChannel,
        flight_number: str = None,
        aircraft: str = None,
        departure: str = None,
        destination: str = None,
        event_link: str = None,
        timestamp: str = None,
    ):
        """
        Create a flight schedule.
        """
        if not all([flight_number, aircraft, departure, destination, event_link, timestamp]):
            await ctx.send("❌ All parameters are required: `channel`, `flight_number`, `aircraft`, `departure`, `destination`, `event_link`, and `timestamp`.")
            return

        # Parse departure and destination
        departure = self.parse_location(departure)
        destination = self.parse_location(destination)
        if departure is None or destination is None:
            await ctx.send(
                "❌ Invalid format for `departure` or `destination`. Both must be enclosed in parentheses, e.g., `(Penang)` or `(Kuantan Airport)`."
            )
            return

        # Parse the timestamp to handle parentheses
        timestamp = self.parse_location(timestamp)
        if timestamp is None:
            await ctx.send(
                "❌ Invalid timestamp format. Enclose the timestamp in parentheses, e.g., `(Monday, December 9, 2024 11:45 PM)` or use a valid Discord timestamp like `<t:1702204800:F>`."
            )
            return

        epoch_time = None
        timestamp_pattern = r"<t:(\d+):?([RFtTdD]?)>"

        if re.match(timestamp_pattern, timestamp):
            epoch_time = int(re.match(timestamp_pattern, timestamp).group(1))
            timestamp_style = re.match(timestamp_pattern, timestamp).group(2)
            if not timestamp_style:
                timestamp = f"<t:{epoch_time}:F>"
        elif timestamp.isdigit():
            epoch_time = int(timestamp)
            timestamp = f"<t:{epoch_time}:F>"
        else:
            try:
                time_struct, _ = self.cal.parse(timestamp)
                naive_time = time.mktime(time_struct)
                local_time = self.timezone.localize(time.localtime(naive_time))
                epoch_time = int(local_time.timestamp())
                timestamp = f"<t:{epoch_time}:F>"
            except Exception:
                await ctx.send(
                    "❌ Invalid timestamp format. Provide a valid natural language date enclosed in parentheses (e.g., `(Monday, December 9, 2024 11:45 PM)`), a Discord timestamp (`<t:1702204800:F>`), or raw epoch time."
                )
                return

        current_time = int(time.time())
        if epoch_time < current_time:
            await ctx.send("❌ Timestamp must be in the future.")
            return

        # Create a unique flight ID
        flight_id = str(uuid.uuid4().int)[:19]

        # Save flight data
        flight_data = {
            "flight_number": flight_number,
            "aircraft": aircraft,
            "departure": departure,
            "destination": destination,
            "event_link": event_link,
            "departure_time": timestamp,
            "channel_id": channel.id,
        }
        self.flights[flight_id] = flight_data

        # Create an embed for the flight schedule
        embed = discord.Embed(
            title="AirAsia Group RBLX | Scheduled Flight",
            description="Details of the flight are shown below.",
            color=discord.Color.from_rgb(255, 0, 0),
        )
        embed.add_field(name="Flight Number", value=flight_number, inline=False)
        embed.add_field(name="Aircraft", value=aircraft, inline=False)
        embed.add_field(name="Departure", value=departure, inline=True)
        embed.add_field(name="Destination", value=destination, inline=True)
        embed.add_field(name="Event Link", value=event_link, inline=False)
        embed.add_field(name="Time", value=timestamp, inline=False)

        await channel.send(embed=embed)
        await ctx.send(f"✅ Flight created successfully with ID: `{flight_id}`")

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def flightlist(self, ctx):
        """
        List all created flights.
        """
        if not self.flights:
            await ctx.send("❌ No flights have been created yet.")
            return

        embed = discord.Embed(
            title="Scheduled Flights",
            description="Here is a list of all scheduled flights:",
            color=discord.Color.blue(),
        )

        for flight_id, data in self.flights.items():
            embed.add_field(
                name=f"{data['flight_number']} ({flight_id})",
                value=(
                    f"**Aircraft:** {data['aircraft']}\n"
                    f"**Departure:** {data['departure']}\n"
                    f"**Destination:** {data['destination']}\n"
                    f"**Time:** {data['departure_time']}\n"
                    f"**Channel:** <#{data['channel_id']}>"
                ),
                inline=False,
            )

        await ctx.send(embed=embed)

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def deleteflight(self, ctx, flight_id: str):
        """
        Delete a flight by its ID.
        """
        if flight_id not in self.flights:
            await ctx.send("❌ Flight ID not found. Please provide a valid flight ID.")
            return

        # Remove the flight from the records
        flight_data = self.flights.pop(flight_id)

        # Notify the user
        await ctx.send(
            f"✅ Flight `{flight_data['flight_number']}` (ID: `{flight_id}`) departing from {flight_data['departure']} to {flight_data['destination']} has been deleted successfully."
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(FlightHosting(bot))
