# SFL Event-Based Activity Point Bot

This Discord bot is designed to manage and track member participation in guild events. It allows event organizers to start events, and participants to join them. The bot automatically calculates and awards "activity points" based on the time a user spends in an event, featuring a server-wide leaderboard to encourage engagement.

## Features

- **Slash Commands**: All interactions with the bot are done through intuitive and easy-to-use Discord slash commands under the `/event` group.
- **Event Management**:
    - Start events with a specific type (e.g., dungeons, PvP, ZvZ).
    - A unique, temporary 4-character join code is generated for each event.
    - Stop events at any time, which automatically calculates points for all participants.
- **Automated Point Calculation**: Points are awarded based on the duration of participation. The rate of points per minute is configurable for each event type.
- **Participant Management**: Event hosts can kick participants if necessary and view a list of everyone currently in their event.
- **Leaderboard & Stats**:
    - Users can check their own total points and a breakdown by event type using `/event me`.
    - A public leaderboard (`/event summary`) displays the top members by activity points.
- **Data Persistence**: The bot saves all data (active events, user points, event logs) to local JSON files, ensuring data integrity across restarts.
- **Configuration**: Event types and point values are easily configured in the `config.json` file.
- **Admin Tools**: Includes commands for administrators to manage user data and create backups.

## Commands

All commands are accessed via the `/event` slash command group.

### User Commands
- `/event start <event_id>`: Starts a new event. The `event_id` corresponds to a pre-configured event type.
- `/event stop`: Stops the event you are currently hosting.
- `/event join <code>`: Joins an active event using its 4-character code.
- `/event kick <member>`: (Host only) Removes a participant from your event.
- `/event list`: (Host only) Shows all participants currently in your event.
- `/event me`: Displays your personal activity point summary.
- `/event id`: Lists all available event IDs and their descriptions.
- `/event summary`: Shows the server-wide activity point leaderboard.

### Admin Commands
- `/admin backup`: Creates a timestamped backup of the data directory.
- `/admin reset_user_data <user>`: Resets all points and event records for a specific user.
- `/admin reset_all_data`: **(DANGEROUS)** Wipes all points and event records for everyone on the server. A confirmation is required.

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ctse2k1/sfl-event-based-ap-bot.git
    cd sfl-event-based-ap-bot
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure the bot:**
    - Rename `.env.example` to `.env`.
    - Open the `.env` file and add your Discord bot token:
      ```
      DISCORD_TOKEN=your_bot_token_here
      ```
    - (Optional) Modify `config.json` to define your own custom events and point values.

4.  **Run the bot:**
    ```bash
    python3 bot.py
    ```

## File Structure

- `bot.py`: The main application file containing all the bot's logic.
- `config.json`: Configuration file for defining event types and points.
- `requirements.txt`: A list of the Python libraries required to run the bot.
- `.env`: File for storing environment variables (like the `DISCORD_TOKEN`).
- `data/`: Directory where the bot stores its persistent data.
    - `active_events.json`: Stores currently running events.
    - `points.json`: Stores user point data.
    - `event_records.json`: Contains a detailed log of all participation.
    - `bot.pid`: A process ID file to prevent multiple instances of the bot from running.
