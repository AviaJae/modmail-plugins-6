import discord
from discord.ext import commands
import uuid
import re  # For timestamp validation
import time  # For epoch conversion

class FlightHosting(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.flights = {}  # Store flights in the format {flight_id: flight_data}

    @commands.command()
    async def createflight(self, ctx, channel: discord.TextChannel, flight_number: str, aircraft: str, departure: str, destination: str, event_link: str, timestamp: str):
        """
        Create a flight schedule.
        Parameters:
        - channel: The channel where the flight message will be posted (mention or ID).
        - flight_number: The flight number (e.g., LMD 917).
        - aircraft: The aircraft model (e.g., B737-800).
        - departure: Departure location.
        - destination: Destination location.
        - event_link: Event link associated with the flight.
        - timestamp: Discord timestamp in <t:epoch:style> format or epoch seconds.
        """
        flight_id = str(uuid.uuid4().int)[:19]  # Generate a unique 19-digit ID

        # Validate and process timestamp
        timestamp_pattern = r"<t:(\d+):?[RFtTdD]?>"  # Matches Discord timestamp formats
        if re.match(timestamp_pattern, timestamp):  # Timestamp in Discord format
            epoch_time = int(re.match(timestamp_pattern, timestamp).group(1))
        elif timestamp.isdigit():  # Raw epoch time
            epoch_time = int(timestamp)
            timestamp = f"<t:{epoch_time}:F>"  # Convert to Discord timestamp format
        else:
            await ctx.send("❌ Invalid timestamp format. Provide a valid Discord timestamp (e.g., `<t:1702204800:F>`) or epoch time.")
            return

        # Check if epoch time is valid
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
        embed = discord.Embed(title="\u2699\ufe0f Flight Schedule", description="AirAsia Group RBLX | Scheduled Flight", color=discord.Color.red())
        embed.set_footer(text="Now Everyone Can Fly")
        embed.add_field(name="\u2708 Flight Number", value=f"**{flight_number}** ({flight_id})", inline=False)
        embed.add_field(name="Location", value=f"{departure} \u2794 {destination}", inline=False)
        embed.add_field(name="Aircraft", value=aircraft, inline=False)
        embed.add_field(name="Departure Time", value=f"{timestamp} (parsed)", inline=False)  # Show both formats
        embed.add_field(name="Event Link", value=event_link, inline=False)

        # Send the embed to the specified channel
        await channel.send(embed=embed)
        await ctx.send(f"✅ Flight created successfully with ID: `{flight_id}`. Message posted in {channel.mention}.")

    @commands.command()
    async def flightlist(self, ctx):
        """
        List all created flights.
        """
        if not self.flights:
            await ctx.send("❌ No flights have been created yet.")
            return

        embed = discord.Embed(title="Flight List", color=discord.Color.green())

        for flight_id, flight_data in self.flights.items():
            embed.add_field(
                name=f"{flight_data['flight_number']} ({flight_id})",
                value=f"**{flight_data['departure']} \u2794 {flight_data['destination']}**\nAircraft: {flight_data['aircraft']}\nDeparture: {flight_data['departure_time']}\nChannel: <#{flight_data['channel_id']}>\n[Event Details]({flight_data['event_link']})",
                inline=False,
            )

        await ctx.send(embed=embed)

    @commands.command()
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

        # Special validation for timestamps and event links
        if field == "departure_time":
            discord_timestamp_regex = r"^<t:\d+(:[a-zA-Z])?>$"
            if not re.match(discord_timestamp_regex, new_value):
                await ctx.send("❌ Invalid departure time. Please use a valid Discord timestamp (e.g., `<t:1738963200:R>`).")
                return
        elif field == "event_link":
            url_regex = r"^(http|https)://[^\s]+$"
            if not re.match(url_regex, new_value):
                await ctx.send("❌ Invalid event link. Please provide a valid URL.")
                return

        flight_data[field] = new_value
        self.flights[flight_id] = flight_data
        await ctx.send(f"✅ Flight `{flight_id}` updated. Field `{field}` is now `{new_value}`.")

async def setup(bot: commands.Bot):
    await bot.add_cog(FlightHosting(bot))
