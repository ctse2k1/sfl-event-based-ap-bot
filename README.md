# SFL Event-Based Activity Point Bot

## 1. Overview

The SFL Event-Based Activity Point Bot is a specialized Discord bot designed to track and reward user participation in timed events. Event hosts can start events with unique join codes, participants manually join using these codes, and the bot automatically calculates points based on participation duration. This system is ideal for gaming communities, guilds, and organizations that want to incentivize engagement and track member activity across various event types.

## 2. Features

- **Event Management:** Start and stop events with unique 4-character join codes
- **Manual Participation Tracking:** Users join events using codes and earn points based on participation time
- **Automated Point Calculation:** Points calculated automatically based on participation duration and event-specific rates
- **Comprehensive Leaderboards:** Server-wide leaderboard ranking users by total points
- **Personal Statistics:** Detailed participation history and total points for individual users
- **Dynamic Event Configuration:** Event types and point values configured via JSON, supporting easy updates without code changes
- **Data Persistence:** All event data stored in organized JSON files with automatic backup functionality
- **Instance Management:** Automatic detection and termination of duplicate bot instances
- **Admin Controls:** Administrative reset functionality with automatic data backup

## 3. Commands

### For Everyone:
- `/event join <code>`: Join an active event using its 4-character code
- `/event me`: View your total activity points and detailed participation history
- `/event summary`: Display the server-wide leaderboard ranking users by total points
- `/event id`: List all available event types and their corresponding IDs
- `/event records`: View a detailed log of recent event participations across all users

### For Event Hosts:
- `/event start <event_id>`: Start a new event and receive a unique join code
- `/event stop`: Stop your current event and finalize points for all participants
- `/event kick <member>`: Remove a participant from your event and calculate their points
- `/event list`: View all current participants in your active event

### For Administrators:
- `/event reset`: Back up and clear all server points and event data (requires Administrator permission)

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

4.  **Configure events:** Edit the `config.json` file to define your event types (see Configuration section below)

5.  **Run the bot:**
    ```bash
    python3 bot.py
    ```

## 5. Configuration

### Bot Configuration (`.env`)
- `DISCORD_TOKEN`: Your Discord application's bot token

### Event Configuration (`config.json`)
The configuration file uses an array structure to define available event types:

```json
{
  "events": [
    {
      "event_id": "101",
      "event_type": "Community Hangout",
      "points_per_minute": 1
    },
    {
      "event_id": "201", 
      "event_type": "Gaming Session",
      "points_per_minute": 2
    }
  ]
}
```

**Configuration Fields:**
- **`event_id`**: Unique string identifier for the event (used with `/event start`)
- **`event_type`**: Descriptive name displayed to users
- **`points_per_minute`**: Points awarded per minute of participation

## 6. Data Storage

The bot creates a `data/` directory containing:
- **`active_events.json`**: Current running events and their participants
- **`event_records.json`**: Historical record of all completed participations
- **`event_records_backup_YYYYMMDD_HHMMSS.json`**: Automatic backups created during resets

## 7. How It Works

1. **Event Creation**: Host uses `/event start <event_id>` to create an event with a unique 4-character code
2. **Participation**: Users join using `/event join <code>` and their participation time begins tracking
3. **Point Calculation**: When users leave (via kick) or event ends, points = duration_minutes × points_per_minute
4. **Data Recording**: All participation records are permanently stored with timestamps and point calculations

## 8. Instance Management

The bot includes automatic instance management that:
- Detects other running instances of the same bot
- Gracefully terminates duplicate instances to prevent conflicts
- Ensures only one bot instance runs at a time
