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
        Extracts text within parentheses for locations (handles spaces in locations).
        E.g., "(Kuantan Airport)" or "(Kuala Lumpur International Airport 2)" -> "Kuantan Airport" or "Kuala Lumpur International Airport 2".
        """
        match = re.match(r"\((.*?)\)", location)
        if match:
            return match.group(1).strip()
        return None

    def parse_time(self, time_string: str) -> str:
        """
        Parses the timestamp provided in brackets into a Discord-compatible timestamp.
        Converts natural language time into epoch time if needed.
        """
        try:
            time_struct, _ = self.cal.parse(time_string)
            naive_time = time.mktime(time_struct)
            local_time = self.timezone.localize(time.localtime(naive_time))
            epoch_time = int(local_time.timestamp())
            return f"<t:{epoch_time}:F>"
        except Exception:
            return None

    async def prompt_user(self, ctx, prompt: str, timeout: int = 30) -> str:
        """
        Prompt the user for input and wait for their response.
        """
        await ctx.send(prompt)
        try:
            response = await self.bot.wait_for(
                "message", check=lambda m: m.author == ctx.author, timeout=timeout
            )
            return response.content.strip()
        except asyncio.TimeoutError:
            await ctx.send(f"❌ You took too long to respond!")
            return None

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def createflight(self, ctx):
        """
        Step-by-step flight creation process.
        """
        # Step 1: Ask for flight number
        flight_number = await self.prompt_user(ctx, "What is the flight number?")
        if not flight_number:
            return

        # Step 2: Ask for aircraft type
        aircraft = await self.prompt_user(ctx, "What is the aircraft type?")
        if not aircraft:
            return

        # Step 3: Ask for departure location
        departure = await self.prompt_user(ctx, "Where is the departure location? (e.g., (Kuantan Airport))")
        if not departure or self.parse_location(departure) is None:
            await ctx.send("❌ Invalid departure format. Ensure it is inside parentheses, e.g., (Kuantan Airport).")
            return
        departure = self.parse_location(departure)

        # Step 4: Ask for destination location
        destination = await self.prompt_user(ctx, "Where is the destination location? (e.g., (Kuala Lumpur International Airport 2))")
        if not destination or self.parse_location(destination) is None:
            await ctx.send("❌ Invalid destination format. Ensure it is inside parentheses, e.g., (Kuala Lumpur International Airport 2).")
            return
        destination = self.parse_location(destination)

        # Step 5: Ask for event link
        event_link = await self.prompt_user(ctx, "What is the event link?")
        if not event_link:
            return

        # Step 6: Ask for departure time
        timestamp = await self.prompt_user(ctx, "What is the departure time? (e.g., (Monday, December 9, 2024 11:45 PM))")
        if not timestamp or self.parse_location(timestamp) is None:
            await ctx.send("❌ Invalid timestamp format. Ensure it is inside parentheses, e.g., (Monday, December 9, 2024 11:45 PM).")
            return
        timestamp = self.parse_location(timestamp)
        discord_timestamp = self.parse_time(timestamp)
        if discord_timestamp is None:
            await ctx.send("❌ Invalid timestamp. Please provide a valid date.")
            return

        # Ensure timestamp is in the future
        current_time = int(time.time())
        epoch_time = int(re.search(r"<t:(\d+):F>", discord_timestamp).group(1))
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
            "departure_time": discord_timestamp,
            "channel_id": ctx.channel.id,
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
        embed.add_field(name="Departure Time", value=f"{discord_timestamp} *(converted to your timezone)*", inline=False)
        embed.add_field(name="Event Link", value=event_link, inline=False)

        await ctx.send(embed=embed)
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
