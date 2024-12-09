@commands.command()
@has_permissions(PermissionLevel.MODERATOR)
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
    timestamp_pattern = r"<t:(\d+):?[RFtTdD]?>"  # Matches Discord timestamp formats
    if re.match(timestamp_pattern, timestamp):  # Timestamp in Discord format
        epoch_time = int(re.match(timestamp_pattern, timestamp).group(1))
    elif timestamp.isdigit():  # Raw epoch time
        epoch_time = int(timestamp)
        timestamp = f"<t:{epoch_time}:F>"  # Convert to Discord timestamp format
    else:
        await ctx.send("❌ Invalid timestamp format. Provide a valid Discord timestamp (e.g., `<t:1702204800:F>`) or epoch time.")
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
