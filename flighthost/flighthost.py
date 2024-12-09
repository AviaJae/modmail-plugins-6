import discord
from discord.ext import commands
import uuid
import time
import re

from core import checks
from core.models import PermissionLevel, DMDisabled, getLogger
from core.time import UserFriendlyTime
from core.paginator import EmbedPaginatorSession, MessagePaginatorSession

class FlightHosting(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.flights = {}  # Store flights in the format {flight_id: flight_data}

    def is_moderator():
        async def predicate(ctx):
            if ctx.author.guild_permissions.manage_messages:
                return True
            await ctx.send("❌ You do not have permission to use this command.")
            return False
        return commands.check(predicate)

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
        Parameters:
        - channel: The channel where the flight message will be posted (mention or ID).
        - flight_number: The flight number (e.g., LMD 917).
        - aircraft: The aircraft model (e.g., B737-800).
        - departure: Departure location (single-word or (multi-word) with parentheses).
        - destination: Destination location (single-word or (multi-word) with parentheses).
        - event_link: Event link associated with the flight.
        - timestamp: Discord timestamp in <t:epoch:style> format or raw epoch seconds.
        """
        # Validate missing arguments
        if not all([flight_number, aircraft, departure, destination, event_link, timestamp]):
            await ctx.send("❌ All parameters are required: `channel`, `flight_number`, `aircraft`, `departure`, `destination`, `event_link`, and `timestamp`.")
            return

        # Parse departure and destination to handle parentheses
        departure = self.parse_location(departure)
        destination = self.parse_location(destination)
        if departure is None or destination is None:
            await ctx.send(
                "❌ Invalid format for `departure` or `destination`. Use single-word locations (e.g., `Penang`) or enclose multi-word locations in parentheses (e.g., `(Kuantan Airport)`)."
            )
            return

        # Generate a unique 19-digit flight ID
        flight_id = str(uuid.uuid4().int)[:19]

        # Validate and process the timestamp
        timestamp_pattern = r"<t:(\d+):?([RFtTdD]?)>"  # Matches Discord timestamp formats (including optional style)
        epoch_time = None
        
        # Check if the timestamp is in Discord format (<t:epoch:style>)
        if re.match(timestamp_pattern, timestamp):  # Discord timestamp format
            epoch_time = int(re.match(timestamp_pattern, timestamp).group(1))
            timestamp_style = re.match(timestamp_pattern, timestamp).group(2)  # Optional style part
            if not timestamp_style:
                timestamp = f"<t:{epoch_time}:F>"  # Default to full date format if style not provided
        elif timestamp.isdigit():  # Raw epoch time
            epoch_time = int(timestamp)
            timestamp = f"<t:{epoch_time}:F>"  # Convert to Discord timestamp format
        else:
            await ctx.send("❌ Invalid timestamp format. Provide a valid Discord timestamp (e.g., `<t:1702204800:F>`) or raw epoch time.")
            return

        # Check if the timestamp is in the future
        current_time = int(time.time())
        if epoch_time < current_time:
            await ctx.send("❌ Timestamp must be in the future.")
            return

        # Save flight details
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

        # Create the embed for the flight schedule
        embed = discord.Embed(
            title="AirAsia Group RBLX | Scheduled Flight",
            description="Details of the flight are shown below.",
            color=discord.Color.from_rgb(255, 0, 0)  # Bright red color
        )
        embed.set_footer(text="AirAsia Group RBLX | All rights reserved.")
        embed.add_field(name="\u2708 Flight Number", value=f"**{flight_number}**", inline=False)
        embed.add_field(name="Location", value=f"{departure} \u2794 {destination}", inline=False)
        embed.add_field(name="Aircraft", value=aircraft, inline=False)
        embed.add_field(name="Departure Time", value=f"{timestamp} (parsed)", inline=False)
        embed.add_field(name="Book Your Flight At", value=f"https://sites.google.com/view/airasiagroupbhd/flights", inline=False)
        embed.add_field(name="Event Link", value=event_link, inline=False)

        # Send the embed to the specified channel
        await channel.send(embed=embed)

        # Send the flight ID privately to the user
        await ctx.send(f"✅ Flight created successfully. Flight ID has been sent privately to you.")
        await ctx.author.send(f"✈️ Flight ID for `{flight_number}`: `{flight_id}`.")

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def flightlist(self, ctx):
        """
        List all created flights.
        """
        if not self.flights:
            await ctx.send("❌ No flights have been created yet.")
            return

        embed = discord.Embed(title="Flight List", color=discord.Color.red())

        for flight_id, flight_data in self.flights.items():
            embed.add_field(
                name=f"{flight_data['flight_number']} ({flight_id})",
                value=f"**{flight_data['departure']} \u2794 {flight_data['destination']}**\nAircraft: {flight_data['aircraft']}\nDeparture: {flight_data['departure_time']}\nChannel: <#{flight_data['channel_id']}>",
                inline=False,
            )

        await ctx.send(embed=embed)

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def deleteflight(self, ctx, flight_id: str):
        """
        Delete a flight using its flight ID.
        """
        if flight_id not in self.flights:
            await ctx.send(f"❌ No flight found with ID: `{flight_id}`.")
            return

        del self.flights[flight_id]
        await ctx.send(f"✅ Flight with ID `{flight_id}` has been deleted.")

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def editflight(self, ctx, flight_id: str, field: str, *, new_value: str):
        """
        Edit an existing flight.
        Fields: flight_number, aircraft, departure, destination, departure_time, event_link
        """
        if flight_id not in self.flights:
            await ctx.send(f"❌ No flight found with ID: `{flight_id}`.")
            return

        flight_data = self.flights[flight_id]

        if field not in flight_data:
            await ctx.send("❌ Invalid field. Valid fields are: flight_number, aircraft, departure, destination, departure_time, event_link.")
            return

        flight_data[field] = new_value
        self.flights[flight_id] = flight_data
        await ctx.send(f"✅ Flight `{flight_id}` updated. Field `{field}` is now `{new_value}`.")

    def parse_location(self, location: str) -> str:
        """
        Parse a location string.
        - If the string is in parentheses (e.g., `(Kuantan Airport)`), return the inner value.
        - If the string is a single word (e.g., `Penang`), return it as is.
        - Return None for invalid formats.
        """
        if location.startswith("(") and location.endswith(")"):
            return location[1:-1].strip()  # Remove parentheses and strip extra spaces
        elif " " not in location:  # Single word
            return location.strip()
        return None  # Invalid format


async def setup(bot: commands.Bot):
    await bot.add_cog(FlightHosting(bot))
