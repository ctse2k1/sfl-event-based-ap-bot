import os
import json
import logging
import discord
from discord.ext import commands
from discord import app_commands, Member, User, Interaction, Embed
from dotenv import load_dotenv
import random
import string
from datetime import datetime, timezone
import atexit
import psutil
import time
import sys
import signal
import shutil
# --- Instance Management ---
def terminate_other_instances():
    """Find and terminate other running instances of this script."""
    current_pid = os.getpid()
    my_name = os.path.basename(__file__)
    logging.info(f"Instance manager started for {my_name} (PID: {current_pid}).")

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Check if process name contains python and script name is in command line
            if 'python' in proc.info['name'].lower() and proc.info['cmdline'] and my_name in proc.info['cmdline'][-1]:
                if proc.pid != current_pid:
                    logging.warning(f"Found another running instance: PID {proc.pid}. Terminating it.")
                    p = psutil.Process(proc.pid)
                    p.terminate() # Send SIGTERM
                    try:
                        p.wait(timeout=3) # Wait for graceful shutdown
                        logging.info(f"Instance {proc.pid} terminated gracefully.")
                    except psutil.TimeoutExpired:
                        logging.warning(f"Instance {proc.pid} did not terminate gracefully. Forcing kill.")
                        p.kill() # Send SIGKILL
                        logging.info(f"Instance {proc.pid} killed.")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
        except Exception as e:
            logging.error(f"Error while checking process {proc.pid}: {e}")

# Run the terminator function at startup
terminate_other_instances()

# --- Basic Logging Setup ---
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)-8s] %(message)s')

# --- Environment Variables ---
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
if not DISCORD_TOKEN:
    logging.error("FATAL: DISCORD_TOKEN not found in .env file.")
    exit()

# --- Constants ---
CONFIG_FILE = 'config.json'
DATA_DIR = 'data'
ACTIVE_EVENTS_FILE = os.path.join(DATA_DIR, 'active_events.json')
EVENT_RECORDS_FILE = os.path.join(DATA_DIR, 'event_records.json')

# --- Ensure Data Directory Exists ---
os.makedirs(DATA_DIR, exist_ok=True)

# --- Helper Functions for Data Persistence ---
def save_data(file_path, data):
    """Saves data to a JSON file with error handling."""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        logging.error(f"Could not write to file {file_path}: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while saving data to {file_path}: {e}")

def load_data(file_path, default_data=None):
    """Loads data from a JSON file, returning default data if not found or invalid."""
    if default_data is None:
        default_data = {}
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        save_data(file_path, default_data)
        return default_data
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logging.warning(f"Could not load data from {file_path}, returning default. Reason: {e}")
        return default_data

# --- Load Initial Data ---
try:
    with open(CONFIG_FILE, 'r') as f:
        EVENT_CONFIGS = {str(event['event_id']): event for event in json.load(f)['events']}
except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
    logging.error(f"FATAL: Could not load or parse {CONFIG_FILE}. Please ensure it exists and is valid. Error: {e}")
    exit()

active_events = load_data(ACTIVE_EVENTS_FILE, {})
event_records_data = load_data(EVENT_RECORDS_FILE, [])

def get_event_by_creator(creator_id):
    """Finds an event hosted by a specific creator."""
    global active_events

    creator_id_str = str(creator_id)
    for event_code, event in active_events.items():
        if event.get('creator_id') == creator_id_str:
            return event_code, event
    return None, None
    return None, None

def calculate_and_finalize_points(member_id, event_code):
    """Calculates points for a user, updates their record, and returns details."""
    global active_events
    global event_records_data

    event = active_events.get(event_code)
    if not event:
        return None

    member_id_str = str(member_id)
    participant_info = event['participants'].get(member_id_str)
    if not participant_info:
        return None

    event_config = EVENT_CONFIGS.get(str(event['event_id']))
    if not event_config:
        return None

    start_time = datetime.fromisoformat(participant_info['join_time'])
    end_time = datetime.now(timezone.utc)
    duration_seconds = (end_time - start_time).total_seconds()
    duration_minutes = duration_seconds / 60
    points = max(0, round(duration_minutes * event_config.get('points_per_minute', 0), 2))

    # Save raw event record
    event_record = {
        'user_id': member_id_str,
        'event_id': event['event_id'],
        'event_type': event_config.get('event_type'),
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'duration_minutes': round(duration_minutes, 2),
        'points_earned': points
    }
    event_records_data.append(event_record)

    return {"points": points, "duration": duration_minutes}

# --- Bot Setup ---
intents = discord.Intents.default()
intents.members = True
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
event_group = app_commands.Group(name="event", description="Manage event activity points.")

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    try:
        bot.tree.add_command(event_group)
        synced = await bot.tree.sync()
        logging.info(f"Synced {len(synced)} commands to Discord.")
    except Exception as e:
        logging.error(f"Error syncing commands: {e}")

# --- Slash Commands ---
@event_group.command(name="start", description="Starts a new event and generates a join code.")
@app_commands.describe(event_id="The unique ID of the event to start.")
async def start(interaction: Interaction, event_id: str):
    global active_events

    creator_id = str(interaction.user.id)
    if get_event_by_creator(creator_id)[0]:
        await interaction.response.send_message("❌ You are already hosting an event. Please stop it first.", ephemeral=True)
        return

    if event_id not in EVENT_CONFIGS:
        await interaction.response.send_message(f"❌ Event ID `{event_id}` is not valid. Use `/event id` to see available IDs.", ephemeral=True)
        return

    event_code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    while event_code in active_events:
        event_code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))

    active_events[event_code] = {
        "creator_id": creator_id,
        "event_id": event_id,
        "start_time": datetime.now(timezone.utc).isoformat(),
        "participants": {
            creator_id: {"join_time": datetime.now(timezone.utc).isoformat()}
        }
    }
    save_data(ACTIVE_EVENTS_FILE, active_events)
    
    embed = Embed(
        title="🎉 Event Started!",
        description=f"Your event `{EVENT_CONFIGS[event_id]['event_type']}` is now active.",
        color=discord.Color.green()
    )
    embed.add_field(name="Join Code", value=f"**`{event_code}`**", inline=False)
    embed.set_footer(text="Participants can now use this code with /event join.")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@event_group.command(name="join", description="Joins an active event using a code.")
@app_commands.describe(code="The 4-character code for the event.")
async def join(interaction: Interaction, code: str):
    global active_events

    event_code = code.lower()
    if event_code not in active_events:
        await interaction.response.send_message("❌ Invalid event code.", ephemeral=True)
        return

    participant_id = str(interaction.user.id)
    if participant_id in active_events[event_code]['participants']:
        await interaction.response.send_message("🤔 You have already joined this event.", ephemeral=True)
        return

    active_events[event_code]['participants'][participant_id] = {"join_time": datetime.now(timezone.utc).isoformat()}
    save_data(ACTIVE_EVENTS_FILE, active_events)
    
    event_id = active_events[event_code]['event_id']
    event_type = EVENT_CONFIGS[event_id]['event_type']
    await interaction.response.send_message(f"✅ You have successfully joined the event: **{event_type}**.", ephemeral=True)

@event_group.command(name="stop", description="Stops the event you are hosting and calculates points.")
async def stop(interaction: Interaction):
    global active_events
    global event_records_data

    creator_id = str(interaction.user.id)
    event_code, event = get_event_by_creator(creator_id)

    if not event:
        await interaction.response.send_message("❌ You are not currently hosting an event.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    
    participant_ids = list(event['participants'].keys())
    for pid in participant_ids:
        calculate_and_finalize_points(pid, event_code)

    del active_events[event_code]
    save_data(EVENT_RECORDS_FILE, event_records_data)
    save_data(ACTIVE_EVENTS_FILE, active_events)
    
    event_type = EVENT_CONFIGS[event['event_id']]['event_type']
    await interaction.followup.send(f"✅ Event `{event_type}` has been stopped. Points have been calculated for all participants.", ephemeral=True)

@event_group.command(name="kick", description="Removes a participant from your event.")
@app_commands.describe(member="The member to remove from the event.")
async def kick(interaction: Interaction, member: Member):
    global active_events

    creator_id = str(interaction.user.id)
    event_code, event = get_event_by_creator(creator_id)

    if not event:
        await interaction.response.send_message("❌ You are not currently hosting an event.", ephemeral=True)
        return

    member_id_str = str(member.id)
    if member_id_str not in event['participants']:
        await interaction.response.send_message(f"❌ {member.display_name} is not in your event.", ephemeral=True)
        return
        
    if member_id_str == creator_id:
        await interaction.response.send_message("❌ You cannot kick yourself. Use `/event stop` to end the event.", ephemeral=True)
        return

    result = calculate_and_finalize_points(member_id_str, event_code)
    del event['participants'][member_id_str]
    save_data(ACTIVE_EVENTS_FILE, active_events)

    points_msg = f"{result['points']:.2f} points" if result else "0 points"
    await interaction.response.send_message(f"✅ {member.display_name} has been kicked and awarded {points_msg}.", ephemeral=True)

@event_group.command(name="list", description="Lists all participants in your current event.")
async def list_participants(interaction: Interaction):
    creator_id = str(interaction.user.id)
    event_code, event = get_event_by_creator(creator_id)

    if not event:
        await interaction.response.send_message("❌ You are not currently hosting an event.", ephemeral=True)
        return

    participant_ids = event['participants'].keys()
    if not participant_ids:
        await interaction.response.send_message("텅 Your event has no participants yet.", ephemeral=True)
        return
        
    participant_list = []
    for pid in participant_ids:
        try:
            member = await interaction.guild.fetch_member(int(pid))
            participant_list.append(member.display_name)
        except (discord.NotFound, discord.HTTPException):
            participant_list.append(f"Unknown User (ID: {pid})")

    event_type = EVENT_CONFIGS[event['event_id']]['event_type']
    embed = Embed(title=f"Participants in '{event_type}'", description="> " + "\n> ".join(participant_list), color=discord.Color.blue())
    await interaction.response.send_message(embed=embed, ephemeral=True)

@event_group.command(name="me", description="Shows your total activity points and event history.")
async def me(interaction: Interaction):
    """Displays all event records of an user."""
    global event_records_data

    if not event_records_data:
        await interaction.response.send_message("You don't have event records yet.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    embed = Embed(
        title=f"{interaction.user.display_name}'s Participation Records",
        description=f"A log of {interaction.user.display_name}'s recorded event participation.",
        color=interaction.user.color
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)

    # Filter out user specific event records
    filtered_records = [d for d in event_records_data if d['user_id'] == str(interaction.user.id)]

    # Sort records by start time, newest first
    sorted_records = sorted(filtered_records, key=lambda x: x['start_time'], reverse=True)

    record_fields = []
    for record in sorted_records:
        event_date = datetime.fromisoformat(record['start_time']).strftime('%Y-%m-%d %H:%M')
        duration_mins = record.get('duration_minutes', 0.0)
        points = record.get('points_earned', 0.0)
        event_type = record.get('event_type', 'Unknown')
        
        field_value = (
            f"**Event:** {event_type}\n"
            f"**Duration:** {duration_mins:.2f} mins\n"
            f"**Points:** {points:.2f}"
        )
        record_fields.append((f"Record - {event_date}", field_value))

    # Add fields to the embed
    for name, value in record_fields:
        embed.add_field(name=name, value=value, inline=False)

    if len(sorted_records) > 20:
        embed.set_footer(text=f"Showing the last 20 of {len(sorted_records)} records.")

    await interaction.followup.send(embed=embed, ephemeral=True)

@event_group.command(name="id", description="Lists all available event IDs and their types.")
async def id(interaction: Interaction):
    if not EVENT_CONFIGS:
        await interaction.response.send_message("No event types are configured.", ephemeral=True)
        return
    
    embed = Embed(title="Available Event IDs & Types", color=discord.Color.blue())
    id_list = [f"`{eid}` - {details['event_type']}" for eid, details in EVENT_CONFIGS.items()]
    embed.description = "\n".join(id_list)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@event_group.command(name="summary", description="Displays the point leaderboard for the server.")
async def summary(interaction: Interaction):
    global event_records_data

    if not event_records_data:
        await interaction.response.send_message("No points have been recorded yet.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    points_data = {}
    for record in event_records_data:
        try:
            user = await interaction.guild.fetch_member(int(record['user_id']))
            user_display_name = user.display_name
        except (NotFound, HTTPException):
            user_display_name = f"Unknown User (ID: {record['user_id']})"

        user_points = points_data.setdefault(user_display_name, {'total_points': 0})
        user_points['total_points'] = user_points['total_points'] + record.get('points_earned', 0.0)

    sorted_users = sorted(points_data.items(), key=lambda item: item[1].get('total_points', 0), reverse=True)

    embed = Embed(title="🏆 Activity Point Leaderboard", color=discord.Color.gold())
    
    if not sorted_users:
        embed.description = "The leaderboard is empty."
        await interaction.followup.send(embed=embed)
        return

    leaderboard_text = ""
    for i, (member_name, data) in enumerate(sorted_users[:50], 1):
        total_points = data.get('total_points', 0)
        leaderboard_text += f"**{i}.** {member_name} - **{total_points:.2f}** points\n"

    embed.description = leaderboard_text
    await interaction.followup.send(embed=embed)

@event_group.command(name="records", description="Shows all event participation records.")
async def records(interaction: Interaction):
    """Displays all event records of all users."""
    global event_records_data

    if not event_records_data:
        await interaction.response.send_message("There are no event records yet.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    embed = Embed(
        title="Event Participation Records",
        description="A log of all recorded event participation.",
        color=0x7289DA  # Discord Blurple
    )

    # Sort records by start time, newest first
    sorted_records = sorted(event_records_data, key=lambda x: x['start_time'], reverse=True)
    
    # Limit to the most recent 20 records to avoid hitting Discord's embed limits
    records_to_display = sorted_records[:20]

    record_fields = []
    for record in records_to_display:
        try:
            user = await interaction.guild.fetch_member(int(record['user_id']))
            user_display_name = user.display_name
        except (NotFound, HTTPException):
            user_display_name = f"Unknown User (ID: {record['user_id']})"

        event_date = datetime.fromisoformat(record['start_time']).strftime('%Y-%m-%d %H:%M')
        duration_mins = record.get('duration_minutes', 0.0)
        points = record.get('points_earned', 0.0)
        event_type = record.get('event_type', 'Unknown')
        
        field_value = (
            f"**User:** {user_display_name}\n"
            f"**Event:** {event_type}\n"
            f"**Duration:** {duration_mins:.2f} mins\n"
            f"**Points:** {points:.2f}"
        )
        record_fields.append((f"Record - {event_date}", field_value))

    # Add fields to the embed
    for name, value in record_fields:
        embed.add_field(name=name, value=value, inline=False)

    if len(sorted_records) > 20:
        embed.set_footer(text=f"Showing the last 20 of {len(sorted_records)} records.")

    await interaction.followup.send(embed=embed, ephemeral=True)

# Enhanced /event reset command to backup and clear event records
@event_group.command(name="reset", description="[ADMIN] Backs up and clears all event data.")
@app_commands.checks.has_permissions(administrator=True)
async def reset(interaction: Interaction):
    """Backs up event records, then clears all active events and recorded points."""
    global active_events
    global event_records_data

    # Backup event_records.json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file_name = f"event_records_backup_{timestamp}.json"
    backup_file_path = os.path.join(DATA_DIR, backup_file_name)

    try:
        if os.path.exists(EVENT_RECORDS_FILE):
            shutil.copy(EVENT_RECORDS_FILE, backup_file_path)
            logging.info(f"Successfully backed up event records to {backup_file_path}")
    except Exception as e:
        logging.error(f"Failed to back up event records: {e}")
        await interaction.response.send_message(
            "\u274c **Error:** Could not back up event records. Reset operation aborted.",
            ephemeral=True
        )
        return

    # Clear data in memory and files
    active_events.clear()
    event_records_data.clear()
    save_data(ACTIVE_EVENTS_FILE, {})
    save_data(EVENT_RECORDS_FILE, [])

    await interaction.response.send_message(
        f"**\u2705 All event data and points have been reset.**\n"
        f"Previous records have been backed up to `{backup_file_name}`.",
        ephemeral=True
    )

@reset.error
async def reset_error(interaction: Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ You do not have permission to use this command.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"An unexpected error occurred: {error}",
            ephemeral=True
        )

# --- Final Bot Run ---
if __name__ == "__main__":
    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN)
