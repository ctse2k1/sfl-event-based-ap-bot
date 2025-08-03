# SFL Event-Based Activity Point Bot

A Discord bot designed to track user participation in server events and automatically award activity points based on time spent. The bot uses slash commands for easy interaction and persists all data locally.

## Features

- **Event Management**: Start, stop, and manage events with unique join codes.
- **Time-Based Points**: Automatically calculates and awards points to participants based on their duration in an event.
- **Persistent Data**: All user points, event records, and active events are saved locally in JSON files, ensuring data is not lost on restart.
- **Leaderboard**: A server-wide leaderboard to foster competition.
- **Individual Stats**: Users can check their own point totals and breakdown by event.
- **Admin Controls**: Secure commands for administrators to reset data, with automatic backups.
- **Instance Locking**: Prevents multiple instances of the bot from running simultaneously.

## Setup & Installation

1.  **Prerequisites**:
    *   Python 3.8+
    *   A Discord Bot Token with `bot` and `applications.commands` scopes. The bot also requires the "Server Members Intent" to be enabled on the Discord Developer Portal.

2.  **Clone the repository**:
    ```bash
    git clone https://github.com/ctse2k1/sfl-event-based-ap-bot.git
    cd sfl-event-based-ap-bot
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create a configuration file for your bot token**:
    *   Create a file named `.env` in the project directory.
    *   Add your bot token to this file:
        ```
        DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN_HERE
        ```

5.  **Define your events**:
    *   Edit the `config.json` file to define the events you want to run. The `event_id` is what you will use with the `/event start` command.
    *   **Example `config.json`**:
        ```json
        {
          "events": [
            {
              "event_id": "1",
              "event_type": "Community Hangout",
              "points_per_minute": 0.5
            },
            {
              "event_id": "2",
              "event_type": "Gaming Session",
              "points_per_minute": 1.0
            }
          ]
        }
        ```

6.  **Run the bot**:
    ```bash
    python bot.py
    ```

## Commands

All commands are accessed via the `/event` slash command group.

### Host Commands

| Command                 | Description                                       | Parameters                               |
| ----------------------- | ------------------------------------------------- | ---------------------------------------- |
| `/event start`          | Starts an event and generates a 4-digit join code. | `event_id`: The ID from `config.json`.   |
| `/event stop`           | Stops the event you are currently hosting.        | _None_                                   |
| `/event kick`           | Removes a participant from your event.            | `member`: The user to kick.              |
| `/event list`           | Lists all participants in your current event.     | _None_                                   |

### Participant Commands

| Command      | Description                          | Parameters                           |
| ------------ | ------------------------------------ | ------------------------------------ |
| `/event join`| Joins an active event.               | `code`: The 4-digit event join code. |
| `/event me`  | Shows your total points and history. | _None_                               |

### General Commands

| Command         | Description                               | Parameters |
| --------------- | ----------------------------------------- | ---------- |
| `/event id`     | Lists all available event IDs and types.  | _None_     |
| `/event summary`| Displays the server point leaderboard.    | _None_     |
| `/event records`| Shows the last 20 event participation logs.| _None_     |

### Admin Commands

| Command       | Description                                  | Permissions   |
| ------------- | -------------------------------------------- | ------------- |
| `/event reset`| **Deletes all data.** Backs up records first. | Administrator |

## Data Files

The bot creates and uses a `data/` directory to store its state:

-   `active_events.json`: Stores information about events that are currently in progress.
-   `points.json`: Contains the total points for each user, broken down by event.
-   `event_records.json`: A detailed log of every single participation record.
-   `bot.pid`: A process ID file to prevent multiple bot instances from running.
-   `event_records_backup_...json`: Created when the `/event reset` command is used.
