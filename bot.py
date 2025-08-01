import os
import json
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import random
import string
from datetime import datetime

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# --- LOAD CONFIGURATION ---
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        EVENT_CONFIGS = {str(event['event_id']): event for event in config['events']}
except FileNotFoundError:
    print("Error: config.json not found. Please create it and restart the bot.")
    exit()
except json.JSONDecodeError:
    print("Error: config.json is not a valid JSON file. Please fix it and restart the bot.")
    exit()

# --- HELPER FUNCTIONS for DATA PERSISTENCE ---
def save_data(file_name, data):
    """Saves data to a JSON file, handling datetime objects."""
    os.makedirs('data', exist_ok=True)
    try:
        with open(os.path.join('data', file_name), 'w') as f:
            def dt_converter(o):
                if isinstance(o, datetime):
                    return o.isoformat()
            json.dump(data, f, indent=4, default=dt_converter)
    except Exception as e:
        print(f"Error saving data to {file_name}: {e}")

def load_data(file_name):
    """Loads data from a JSON file, returning an empty dict if not found or invalid."""
    file_path = os.path.join('data', file_name)
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            if not content:
                return {}
            return json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

# --- HELPER FUNCTION for POINTS CALCULATION ---
def calculate_points(start_time, end_time, ppm):
    """Calculates points based on duration and points per minute."""
    if isinstance(start_time, str):
        start_time = datetime.fromisoformat(start_time)
    if isinstance(end_time, str):
        end_time = datetime.fromisoformat(end_time)
    duration_seconds = (end_time - start_time).total_seconds()
    duration_minutes = duration_seconds / 60
    return max(0, round(duration_minutes * ppm, 2)), max(0, round(duration_minutes, 2))

# --- BOT SETUP ---
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    """Event handler for when the bot logs in and is ready."""
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    try:
        print("Attempting to sync the following commands:")
        command_list_str = []
        for command in bot.tree.get_commands():
            if isinstance(command, app_commands.Group):
                command_list_str.append(f"- Command Group: {command.name}")
                for subcommand in command.commands:
                    command_list_str.append(f"  - Subcommand: {subcommand.name}")
        print('\n'.join(sorted(command_list_str)))
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command groups to Discord.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    print('------')

# --- SLASH COMMANDS ---
event_group = app_commands.Group(name="event", description="Commands for managing event activity points.")

@event_group.command(name="start", description="Starts an event and generates an event code.")
@app_commands.describe(event_id="The ID of the event from the config file.")
async def start(interaction: discord.Interaction, event_id: str):
    await interaction.response.defer(ephemeral=True)
    creator_id = str(interaction.user.id)
    active_events = load_data("active_events.json")
    
    if any(event['creator_id'] == creator_id for event in active_events.values()):
        await interaction.followup.send("You are already hosting an event. Use `/event stop` to end it first.", ephemeral=True)
        return

    if event_id not in EVENT_CONFIGS:
        await interaction.followup.send(f"Event ID `{event_id}` is invalid. Please check `config.json`.", ephemeral=True)
        return

    event_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    while event_code in active_events:
        event_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

    active_events[event_code] = {
        "event_id": event_id,
        "creator_id": creator_id,
        "start_time": datetime.utcnow(),
        "participants": {}
    }
    save_data("active_events.json", active_events)
    
    event_type = EVENT_CONFIGS[event_id]['event_type']
    await interaction.followup.send(f"Event '{event_type}' started! Your members can join with the code: **{event_code}**", ephemeral=True)
    await interaction.channel.send(f"🎉 **{interaction.user.display_name}** has started the event: **'{event_type}'**! Join with the code provided by the host.")

@event_group.command(name="join", description="Join an active event using the event code.")
@app_commands.describe(event_code="The 4-character code for the event.")
async def join(interaction: discord.Interaction, event_code: str):
    await interaction.response.defer(ephemeral=True)
    user_id = str(interaction.user.id)
    code = event_code.upper()
    active_events = load_data("active_events.json")

    if code not in active_events:
        await interaction.followup.send("Invalid event code.", ephemeral=True)
        return

    event = active_events[code]
    if user_id == event['creator_id']:
        await interaction.followup.send("You cannot join your own event as a participant.", ephemeral=True)
        return
    if user_id in event['participants']:
        await interaction.followup.send("You have already joined this event.", ephemeral=True)
        return

    event['participants'][user_id] = datetime.utcnow()
    save_data("active_events.json", active_events)
    event_type = EVENT_CONFIGS[event['event_id']]['event_type']
    await interaction.followup.send(f"You have successfully joined the event: '{event_type}'.", ephemeral=True)

@event_group.command(name="stop", description="Stops the current event you created.")
async def stop(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)
    creator_id = str(interaction.user.id)
    active_events = load_data("active_events.json")
    event_records = load_data("event_records.json")
    event_code = next((code for code, event in active_events.items() if event['creator_id'] == creator_id), None)

    if not event_code:
        await interaction.followup.send("You are not hosting an event.", ephemeral=True)
        return

    event = active_events[event_code]
    event_config = EVENT_CONFIGS[event['event_id']]
    ppm = event_config['points_per_minute']
    end_time = datetime.utcnow()
    
    creator_start_time = datetime.fromisoformat(event['start_time'])
    creator_points, creator_duration = calculate_points(creator_start_time, end_time, ppm)
    if creator_id not in event_records: event_records[creator_id] = []
    event_records[creator_id].append({"event_type": event_config['event_type'], "points_earned": creator_points, "duration_minutes": creator_duration})

    for user_id, join_time_str in event['participants'].items():
        join_time = datetime.fromisoformat(join_time_str)
        points, duration = calculate_points(join_time, end_time, ppm)
        if user_id not in event_records: event_records[user_id] = []
        event_records[user_id].append({"event_type": event_config['event_type'], "points_earned": points, "duration_minutes": duration})

    del active_events[event_code]
    save_data("active_events.json", active_events)
    save_data("event_records.json", event_records)
    await interaction.followup.send(f"Event '{event_config['event_type']}' has been stopped. All points have been calculated and stored.", ephemeral=False)

@event_group.command(name="kick", description="Kicks a participant from your event.")
@app_commands.describe(member="The member to kick.")
async def kick(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer(ephemeral=True)
    creator_id = str(interaction.user.id)
    user_to_kick_id = str(member.id)
    active_events = load_data("active_events.json")
    event_records = load_data("event_records.json")
    event_code = next((code for code, event in active_events.items() if event['creator_id'] == creator_id), None)

    if not event_code:
        await interaction.followup.send("You are not hosting an event.", ephemeral=True)
        return

    event = active_events[event_code]
    if user_to_kick_id not in event['participants']:
        await interaction.followup.send(f"{member.display_name} is not in your event.", ephemeral=True)
        return

    event_config = EVENT_CONFIGS[event['event_id']]
    ppm = event_config['points_per_minute']
    end_time = datetime.utcnow()
    join_time = datetime.fromisoformat(event['participants'][user_to_kick_id])
    points, duration = calculate_points(join_time, end_time, ppm)

    if user_to_kick_id not in event_records: event_records[user_to_kick_id] = []
    event_records[user_to_kick_id].append({"event_type": event_config['event_type'], "points_earned": points, "duration_minutes": duration})
    
    del event['participants'][user_to_kick_id]
    save_data("active_events.json", active_events)
    save_data("event_records.json", event_records)
    await interaction.followup.send(f"You have kicked {member.display_name}. They have been awarded {points:.2f} points for their participation.", ephemeral=True)

@event_group.command(name="list", description="Lists participants in your current event.")
async def list_participants(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    creator_id = str(interaction.user.id)
    active_events = load_data("active_events.json")
    event_code = next((code for code, event in active_events.items() if event['creator_id'] == creator_id), None)

    if not event_code:
        await interaction.followup.send("You are not currently hosting an event.", ephemeral=True)
        return

    participants_list = active_events[event_code].get('participants', {})
    if not participants_list:
        await interaction.followup.send("No one has joined your event yet.", ephemeral=True)
        return

    event_config = EVENT_CONFIGS[active_events[event_code]['event_id']]
    embed = discord.Embed(title=f"Participants in '{event_config['event_type']}'", description=f"Event Code: **{event_code}**", color=discord.Color.blue())
    details = []
    now = datetime.utcnow()
    for user_id, join_time_str in participants_list.items():
        try:
            user = await bot.fetch_user(int(user_id))
            join_time = datetime.fromisoformat(join_time_str)
            duration = now - join_time
            hours, rem = divmod(duration.total_seconds(), 3600)
            mins, _ = divmod(rem, 60)
            details.append(f"• **{user.display_name}** (Joined for {int(hours)}h {int(mins)}m)")
        except (discord.NotFound, ValueError):
            details.append(f"• Unknown User (`{user_id}`)")
    if details:
        embed.add_field(name="Current Participants", value="\n".join(details), inline=False)
    await interaction.followup.send(embed=embed, ephemeral=True)

@event_group.command(name="me", description="Shows your own event points and total points.")
async def me(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        user_id = str(interaction.user.id)
        all_data = load_data(RECORDS_FILE)
        user_records = [rec for rec in all_data.get("records", []) if rec.get("user_id") == user_id]

        if not user_records:
            await interaction.followup.send("You have no event records yet.", ephemeral=True)
            return

        total_points = sum(rec.get("points", 0) for rec in user_records)

        embed = discord.Embed(
            title=f"{interaction.user.display_name}'s Activity Points",
            description="A summary of your event participation.",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="🏆 Total Points", value=f"**{total_points}**", inline=False)
        embed.add_field(name="\u200b", value="\u200b", inline=False)

        for record in user_records[:22]:  # Limit to 22 to fit in a single embed
            embed.add_field(name=f"Event: {record.get('event_id', 'N/A')}", value=f"Points: {record.get('points', 0)}", inline=True)

        await interaction.followup.send(embed=embed, ephemeral=True)
    except Exception as e:
        print(f"Error in /event me command: {e}")
        await interaction.followup.send("An error occurred while fetching your records. Please try again later.", ephemeral=True)

@event_group.command(name="id", description="Lists all available event IDs and their types.")
async def event_id_list(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        with open(CONFIG_FILE, 'r') as f:
            config_data = json.load(f)
        
        events = config_data.get("events", [])

        if not events:
            await interaction.followup.send("No events found in the configuration file.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Available Event IDs",
            description="Here is a list of all configured events.",
            color=discord.Color.purple()
        )

        for event in events:
            embed.add_field(name=f"ID: {event.get('event_id', 'N/A')}", value=f"Type: {event.get('event_type', 'N/A')}", inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)
    except FileNotFoundError:
        await interaction.followup.send(f"Error: The configuration file (`{CONFIG_FILE}`) was not found.", ephemeral=True)
    except json.JSONDecodeError:
        await interaction.followup.send(f"Error: The configuration file (`{CONFIG_FILE}`) is not a valid JSON file.", ephemeral=True)
    except Exception as e:
        print(f"Error in /event id command: {e}")
        await interaction.followup.send("An unexpected error occurred while fetching the event IDs.", ephemeral=True)

@event_group.command(name="records", description="Displays activity point records for all members (Admin only).")
@app_commands.checks.has_permissions(administrator=True)
async def records(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    all_records = load_data("event_records.json")

    if not all_records:
        await interaction.followup.send("There are no event records yet.", ephemeral=True)
        return

    embed = discord.Embed(title="All Member Activity Records", color=discord.Color.orange())
    for user_id, user_records in all_records.items():
        try:
            user = await bot.fetch_user(int(user_id))
            display_name = user.display_name
        except (discord.NotFound, ValueError):
            display_name = f"Unknown User ({user_id})"
        record_details = [f"  - {rec.get('event_type', 'Unknown')}: {rec.get('points_earned', 0):.2f} pts" for rec in user_records]
        if record_details:
            embed.add_field(name=f"👤 {display_name}", value="\n".join(record_details), inline=False)
    await interaction.followup.send(embed=embed, ephemeral=True)

@event_group.command(name="summary", description="Shows a leaderboard of total points.")
async def summary(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)
    all_records = load_data("event_records.json")
    if not all_records:
        await interaction.followup.send("There are no event records to summarize.", ephemeral=True)
        return

    leaderboard = {user_id: sum(r.get('points_earned', 0) for r in recs) for user_id, recs in all_records.items()}
    if not any(leaderboard.values()):
        await interaction.followup.send("No points have been awarded yet.", ephemeral=True)
        return

    sorted_leaderboard = sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)
    embed = discord.Embed(title="🏆 Event Points Leaderboard 🏆", color=discord.Color.gold())
    description = []
    medals = ["🥇", "🥈", "🥉"]
    for i, (user_id, total_points) in enumerate(sorted_leaderboard[:10]):
        try:
            user = await bot.fetch_user(int(user_id))
            display_name = user.display_name
        except (discord.NotFound, ValueError):
            display_name = f"Unknown User ({user_id})"
        prefix = medals[i] if i < 3 else f"**#{i+1}**"
        description.append(f"{prefix} {display_name}: **{total_points:.2f} points**")
    embed.description = "\n".join(description)
    await interaction.followup.send(embed=embed)

@event_group.command(name="reset", description="Clears all event data (Admin only).")
@app_commands.checks.has_permissions(administrator=True)
async def reset(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    save_data("active_events.json", {})
    save_data("event_records.json", {})
    await interaction.followup.send("All event data has been reset.", ephemeral=True)

@reset.error
@records.error
async def permission_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
    else:
        print(f"An error occurred in a command: {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)
        else:
            await interaction.followup.send("An unexpected error occurred.", ephemeral=True)

bot.tree.add_command(event_group)

if DISCORD_TOKEN and DISCORD_TOKEN != "YOUR_DISCORD_BOT_TOKEN":
    bot.run(DISCORD_TOKEN)
else:
    print("FATAL: DISCORD_TOKEN is not set or is still the default value. Please check your .env file.")
