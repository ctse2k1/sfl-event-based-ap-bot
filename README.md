# SFL Event-Based Activity Point Bot

## 1. Overview

The SFL Event-Based Activity Point Bot is a specialized Discord bot designed to track and reward user participation in voice channel events. It allows event managers to start and stop events, automatically recording the time users spend in a designated voice channel and awarding them points based on pre-configured rates. This bot is ideal for communities that host regular events and want to incentivize engagement.

## 2. Features

- **Event Management:** Start and stop events.
- **Automated Point Calculation:** Automatically calculates and awards points to participants based on their duration in a voice channel during an event.
- **Leaderboard:** Display a server-wide leaderboard of user points.
- **Personal Statistics:** Users can check their own participation history and total points.
- **Dynamic Event Configuration:** Event types and point values are configured via a simple JSON file, allowing for easy updates without code changes.
- **Data Persistence:** Event participation data is saved locally in a JSON file, ensuring no data is lost between bot restarts.

## 3. Commands

### For Everyone:
- `/event join <code>`: Joins an event using a 4-character code.
- `/event me`: Shows your total activity points and a detailed history of your event participation.
- `/event summary`: Displays the server-wide leaderboard, ranking users by their total points.
- `/event id`: Lists all available event types and their corresponding IDs.
- `/event records`: Shows a detailed log of the most recent event participations.

### For Event Hosts:
- `/event start <event_id>`: Starts a new event.
- `/event stop`: Stops the event you are hosting and calculates points.
- `/event kick <member>`: Removes a participant from your event.
- `/event list`: Lists all participants in your current event.
- `/event reset`: (Admin only) Backs up and clears all server points and event data.

## 4. Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ctse2k1/sfl-event-based-ap-bot.git
    cd sfl-event-based-ap-bot
    ```

2.  **Install dependencies:**
    ```bash
    pip3 install -r requirements.txt
    ```

3.  **Create a `.env` file** in the project root and add your Discord bot token:
    ```
    DISCORD_TOKEN=your_bot_token_here
    ```

4.  **Configure events:** Edit the `config.json` file to define your events.

5.  **Run the bot:**
    ```bash
    python3 bot.py
    ```

## 5. Configuration

### Bot Configuration (`.env`)
- `DISCORD_TOKEN`: Your Discord application's bot token.

### Event Configuration (`config.json`)
This file defines the types of events the bot can manage.

- **`event_id`**: A unique integer identifier for the event. This is what you use with the `/event start` command.
- **`event_type`**: A descriptive name for the event (e.g., "Community Hangout", "Gaming Night").
- **`points_per_minute`**: The number of points a user earns for each minute of participation.

**Example `config.json`:**
```json
{
  "1": {
    "event_type": "Community Hangout",
    "points_per_minute": 0.5
  },
  "2": {
    "event_type": "Gaming Night",
    "points_per_minute": 1.0
  }
}
```
