# SFL Event-Based Activity Point Bot

**Version:** `v0.0.8`

This Discord bot allows server members to earn activity points by participating in events. Event hosts can start and stop events, and the bot will automatically track participation time and award points accordingly. It features a leaderboard, personal point tracking, and administrative controls.

## ✨ Features

- **Event Management**: Start, stop, and manage events with simple commands.
- **Automatic Point Calculation**: Points are awarded based on the time spent in an event.
- **Unique Join Codes**: Each event has a unique, randomly generated 4-character code for joining.
- **Leaderboard**: Display a server-wide leaderboard of top point earners.
- **Personal Stats**: Users can check their own total points and breakdown by event.
- **Admin Controls**: Secure commands for resetting data and viewing participation records.
- **Data Persistence**: All points and event data are saved locally in a `data` directory.

- **Admin Controls**: Secure command for resetting data.

### Prerequisites

- Python 3.8+
- A Discord Bot Token

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ctse2k1/sfl-event-based-ap-bot.git
    cd sfl-event-based-ap-bot
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration:**
    - Rename the `.env.example` file to `.env` (if applicable) or create a new `.env` file.
    - Add your Discord bot token to the `.env` file:
      ```
      DISCORD_TOKEN=YOUR_BOT_TOKEN_HERE
      ```
    - Customize event types by editing the `config.json` file. See the [Software Specification](SOFTWARE_SPECIFICATION.md) for details on the configuration format.

4.  **Run the bot:**
    ```bash
    python bot.py
    ```

## 🤖 Bot Commands

All commands are accessed via the `/event` slash command group.

-   `/event start <event_id>`: Starts an event you will host. The bot provides a unique join code.
-   `/event join <code>`: Join an active event using its 4-character code.
-   `/event records`: Shows a detailed log of the most recent event participations.
-   `/event kick <member>`: (Host only) Removes a participant from your event and calculates their points.
-   `/event list`: (Host only) Shows a list of all participants in your current event.
-   `/event me`: Check your personal total points and a summary of points per event.
-   `/event id`: View a list of all available event IDs and their types.
-   `/event summary`: Displays the server-wide activity point leaderboard.
-   `/event records`: (Admin only) Shows a detailed log of the most recent event participations.
-   `/event reset`: (Admin only) Backs up and clears all server points and event data.

---
*This bot is designed to be simple, robust, and easy to manage for community engagement.*
