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
POINTS_FILE = os.path.join(DATA_DIR, 'points.json')

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
points_data = load_data(POINTS_FILE, {})

# --- Core Logic Functions ---
def get_event_by_creator(creator_id):
    """Finds an event hosted by a specific creator."""
    creator_id_str = str(creator_id)
    for event_code, event in active_events.items():
        if event.get('creator_id') == creator_id_str:
            return event_code, event
    return None, None

def calculate_and_finalize_points(member_id, event_code):
    """Calculates points for a user, updates their record, and returns details."""
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

    # Update points data
    user_points = points_data.setdefault(member_id_str, {'total_points': 0, 'events': {}})
    event_id_str = str(event['event_id'])
    user_points['events'][event_id_str] = user_points['events'].get(event_id_str, 0) + points
    user_points['total_points'] = round(sum(user_points['events'].values()), 2)
    
    save_data(POINTS_FILE, points_data)
    
    return {"points": points, "duration": duration_minutes}

# --- Bot Setup ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
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
    creator_id = str(interaction.user.id)
    if get_event_by_creator(creator_id)[0]:
        await interaction.response.send_message("❌ You are already hosting an event. Please stop it first.", ephemeral=True)
        return

    if event_id not in EVENT_CONFIGS:
        await interaction.response.send_message(f"❌ Event ID `{event_id}` is not valid. Use `/event id` to see available IDs.", ephemeral=True)
        return

    event_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    while event_code in active_events:
        event_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

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
    event_code = code.upper()
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
    save_data(ACTIVE_EVENTS_FILE, active_events)
    
    event_type = EVENT_CONFIGS[event['event_id']]['event_type']
    await interaction.followup.send(f"✅ Event **{event_type}** has been stopped. Points awarded to all participants.", ephemeral=True)

@event_group.command(name="kick", description="Removes a participant from your event.")
@app_commands.describe(member="The member to remove from the event.")
async def kick(interaction: Interaction, member: Member):
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
        member = interaction.guild.get_member(int(pid))
        participant_list.append(member.display_name if member else f"Unknown User (ID: {pid})")

    event_type = EVENT_CONFIGS[event['event_id']]['event_type']
    embed = Embed(title=f"Participants in '{event_type}'", description="> " + "\n> ".join(participant_list), color=discord.Color.blue())
    await interaction.response.send_message(embed=embed, ephemeral=True)

@event_group.command(name="me", description="Shows your total activity points and event history.")
async def me(interaction: Interaction):
    user_id = str(interaction.user.id)
    user_data = points_data.get(user_id)

    if not user_data or not user_data.get('events'):
        await interaction.response.send_message("You have not participated in any events yet.", ephemeral=True)
        return

    embed = Embed(title="Your Activity Points", color=discord.Color.purple())
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
    embed.add_field(name="Total Points", value=f"**{user_data.get('total_points', 0):.2f}**", inline=False)

    event_details = []
    for event_id, points in user_data['events'].items():
        event_type = EVENT_CONFIGS.get(event_id, {}).get('event_type', 'Unknown Event')
        event_details.append(f"**{event_type}**: {points:.2f} points")
    
    if event_details:
        embed.add_field(name="Points by Event", value="\n".join(event_details), inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@event_group.command(name="id", description="Lists all available event IDs and their types.")
async def id(interaction: Interaction):
    if not EVENT_CONFIGS:
        await interaction.response.send_message("No event types are configured.", ephemeral=True)
        return
    
    embed = Embed(title="Available Event Types", color=discord.Color.teal())
    id_list = [f"`{eid}` - {details['event_type']}" for eid, details in EVENT_CONFIGS.items()]
    embed.description = "\n".join(id_list)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@event_group.command(name="records", description="Shows a detailed record of points for each user.")
async def records(interaction: Interaction):
    if not points_data:
        await interaction.response.send_message("No points have been recorded yet.", ephemeral=True)
        return

    embed = Embed(title="Detailed Point Records", color=discord.Color.blue())
    
    records_text = []
    sorted_users = sorted(points_data.items(), key=lambda item: item[1].get('total_points', 0), reverse=True)

    for user_id, data in sorted_users:
        member = interaction.guild.get_member(int(user_id))
        name = member.display_name if member else f"Unknown User (ID: {user_id})"
        total_points = data.get('total_points', 0)
        
        user_record = f"**{name}** - Total: {total_points:.2f} Points\n"
        
        event_details = []
        if 'events' in data:
            for event_id, points in data['events'].items():
                event_type = EVENT_CONFIGS.get(event_id, {}).get('event_type', 'Unknown Event')
                event_details.append(f"  - `{event_type}`: {points:.2f} points")
        
        if event_details:
            user_record += "\n".join(event_details)
        else:
            user_record += "  - No specific event points recorded."

        records_text.append(user_record)

    if not records_text:
        await interaction.response.send_message("No point records found.", ephemeral=True)
        return

    embed.description = "\n\n".join(records_text)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@event_group.command(name="summary", description="Displays the point leaderboard for the server.")
async def summary(interaction: Interaction):
    if not points_data:
        await interaction.response.send_message("No points have been recorded yet.", ephemeral=True)
        return

    sorted_users = sorted(points_data.items(), key=lambda item: item[1].get('total_points', 0), reverse=True)
    
    embed = Embed(title="🏆 Activity Point Leaderboard", color=discord.Color.gold())
    
    description = []
    for i, (user_id, data) in enumerate(sorted_users[:20]): # Limit to top 20
        member = interaction.guild.get_member(int(user_id))
        name = member.display_name if member else f"Unknown User (ID: {user_id})"
        points = data.get('total_points', 0)
        description.append(f"**{i+1}. {name}** - {points:.2f} Points")
        
    if not description:
        await interaction.response.send_message("The leaderboard is empty.", ephemeral=True)
        return

    embed.description = "\n".join(description)
    await interaction.response.send_message(embed=embed, ephemeral=True)
@event_group.command(name="reset", description="[Admin Only] Resets all event data and points.")
@app_commands.checks.has_permissions(administrator=True)
async def reset(interaction: Interaction):
    global active_events, points_data
    
    # Clear in-memory data
    active_events.clear()
    points_data.clear()
    
    # Clear data files
    save_data(ACTIVE_EVENTS_FILE, {})
    save_data(POINTS_FILE, {})
    
    logging.warning(f"All data has been reset by {interaction.user} (ID: {interaction.user.id}).")
    await interaction.response.send_message("✅ All event and point data has been successfully reset.", ephemeral=True)

@reset.error
async def on_reset_error(interaction: Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)
        logging.error(f"Error in /reset command: {error}")

# --- Run Bot ---
if __name__ == "__main__":
    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN)
    else:
        logging.error("Bot could not start: DISCORD_TOKEN is not set.")
