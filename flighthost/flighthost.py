import discord
from discord.ext import commands
import uuid
import time
import pytz
import parsedatetime
import re

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
        This function now returns the location directly without requiring parentheses.
        """
        return location.strip() if location else None

    async def prompt_for_input(self, ctx, question: str, timeout: int = 30) -> str:
        """
        Prompt the user for input and return their response. 
        The function will timeout after a specified time.
        """
        await ctx.send(question)
        try:
            response = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author, timeout=timeout)
            return response.content
        except asyncio.TimeoutError:
            await ctx.send("❌ Time's up! Please try again.")
            return None

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def createflight(
        self,
        ctx,
        channel: discord.TextChannel,
    ):
        """
        Step-by-step creation of a flight schedule with restart option and timeout.
        """
        # Step 1: Ask for flight number
        flight_number = await self.prompt_for_input(ctx, "What is the flight number? (You have 30 seconds to respond.)")
        if flight_number is None:
            return

        # Step 2: Ask for aircraft
        aircraft = await self.prompt_for_input(ctx, "What is the aircraft? (You have 30 seconds to respond.)")
        if aircraft is None:
            return

        # Step 3: Ask for departure
        departure = await self.prompt_for_input(ctx, "Where is the departure location? (You have 30 seconds to respond.)")
        if departure is None:
            return
        departure = self.parse_location(departure)

        # Step 4: Ask for destination
        destination = await self.prompt_for_input(ctx, "Where is the destination location? (You have 30 seconds to respond.)")
        if destination is None:
            return
        destination = self.parse_location(destination)

        # Step 5: Ask for event link
        event_link = await self.prompt_for_input(ctx, "Please provide the event link. (You have 30 seconds to respond.)")
        if event_link is None:
            return

        # Step 6: Ask for timestamp
        timestamp = await self.prompt_for_input(ctx, "Please provide the timestamp for the flight. (You have 30 seconds to respond.)")
        if timestamp is None:
            return

        # Parse the departure, destination, and timestamp directly without parentheses
        if not departure or not destination or not timestamp:
            await ctx.send("❌ All fields are required.")
            return

        # Parse the timestamp to handle different formats
        epoch_time = None
        timestamp_pattern = r"<t:(\d+):?([RFtDd]?)>"

        if re.match(timestamp_pattern, timestamp):  # Discord timestamp format
            epoch_time = int(re.match(timestamp_pattern, timestamp).group(1))
            timestamp_style = re.match(timestamp_pattern, timestamp).group(2)
            if not timestamp_style:
                timestamp = f"<t:{epoch_time}:F>"
        elif timestamp.isdigit():  # If it's a direct epoch time
            epoch_time = int(timestamp)
            timestamp = f"<t:{epoch_time}:F>"
        else:  # Natural language timestamp
            try:
                time_struct, _ = self.cal.parse(timestamp)
                naive_time = time.mktime(time_struct)
                local_time = self.timezone.localize(time.localtime(naive_time))
                epoch_time = int(local_time.timestamp())
                timestamp = f"<t:{epoch_time}:F>"
            except Exception:
                await ctx.send(
                    "❌ Invalid timestamp format. Please provide a valid natural language date or a Discord timestamp."
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
        embed.add_field(name="Departure Time", value=f"{timestamp} *(converted to your timezone)*", inline=False)
        embed.add_field(name="Book Your Flight At", value=f"https://sites.google.com/view/airasiagroupbhd/flights", inline=False)
        embed.add_field(name="Event Link", value=event_link, inline=False)

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
                value=(f"**Aircraft:** {data['aircraft']}\n"
                       f"**Departure:** {data['departure']}\n"
                       f"**Destination:** {data['destination']}\n"
                       f"**Time:** {data['departure_time']}\n"
                       f"**Channel:** <#{data['channel_id']}>"),
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
