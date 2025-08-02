# SFL Event-based Activity Points Bot

The **SFL Event-based Activity Points Bot** is a Discord bot designed to track and reward member participation in server events. It allows event organizers to manage events, track attendance, and automatically calculate and assign activity points based on configurable parameters.

## Key Features

- **Event Management**: Start and stop events with simple slash commands.
- **Automated Point Calculation**: Points are calculated based on participation duration and event-specific rates.
- **Unique Join Codes**: Each event has a unique, temporary code for participants to join.
- **Flexible Configuration**: Event types and point rates are defined in a `config.json` file.
- **Persistent Data**: All event data and member points are saved locally.
- **Leaderboards**: Display server-wide rankings based on total points.
- **Per-Server Profiles**: Uses server-specific display names and avatars.

## Slash Commands

The bot uses a main command group named `/event`.

### Event Management
- `/event start <event_id>`: Starts a new event and generates a 4-character join code. Only one event can be hosted by a user at a time.
- `/event stop`: Stops the currently hosted event, calculates points for all participants, and saves the data.
- `/event kick <member>`: Removes a participant from the event and calculates their points.
- `/event list`: Shows a list of all participants currently in the event you are hosting.

### Participant Commands
- `/event join <code>`: Allows a member to join an active event using its 4-character code.
- `/event me`: Displays your own total activity points and a breakdown of points per event.

### Informational Commands
- `/event id`: Lists all available event IDs and their corresponding types from the configuration file.
- `/event summary`: Shows a server-wide leaderboard of members ranked by total activity points.
- `/event records <member>`: Displays a detailed breakdown of points for a specific member.

### Administrative Commands
- `/event reset`: (Administrator Only) Clears all active event data and resets all member points to zero.

## Setup & Configuration

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ctse2k1/sfl-event-based-ap-bot.git
    cd sfl-event-based-ap-bot
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Create a `.env` file** in the root directory and add your Discord bot token:
    ```
    DISCORD_TOKEN=YOUR_BOT_TOKEN_HERE
    ```

4.  **Configure events** in `config.json`. Define your events with an ID, type, and points-per-minute rate.
    ```json
    {
      "events": [
        {
          "event_id": 101,
          "event_type": "Community Hangout",
          "points_per_minute": 1.5
        },
        {
          "event_id": 201,
          "event_type": "Gaming Night",
          "points_per_minute": 2.0
        }
      ]
    }
    ```

5.  **Run the bot:**
    ```bash
    python3 bot.py
    ```

## Data Persistence

- **Active Events**: Stored in `data/active_events.json`.
- **Member Points**: Stored in `data/points.json`.

The `data` directory is created automatically if it doesn't exist.
