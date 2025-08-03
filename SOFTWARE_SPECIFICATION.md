# Software Specification: SFL Event-Based Activity Point Bot

**Version:** `v0.0.8`

## 1. Introduction

This document outlines the software specifications for the SFL Event-Based Activity Point Bot. The bot is designed to run on Discord and allows server administrators to reward users with points for participating in designated events. The system is event-driven, with points calculated based on the duration of participation.

## 2. System Architecture

The bot is a single-instance Python application that connects to the Discord API via the `discord.py` library.

-   **Language**: Python 3
-   **Primary Library**: `discord.py`
-   **Data Storage**: Local JSON files within a `data/` directory.
-   **Configuration**: A root `config.json` file for event definitions and a `.env` file for sensitive credentials (Discord Token).

### 2.1. Data Persistence

The bot maintains its state through several JSON files located in the `data/` directory:

-   `active_events.json`: Stores a dictionary of currently running events, including the host, participants, and start times.
-   `points.json`: Stores a dictionary mapping user IDs to their total points and a breakdown of points per event type.
-   `event_records.json`: A list of all historical participation records, logging user, event details, duration, and points earned.
-   `bot.pid`: A process ID file to prevent multiple instances of the bot from running simultaneously.

Data is loaded into memory on startup and saved back to the disk whenever a state change occurs (e.g., a user joins an event, an event is stopped).

## 3. Core Functionality

### 3.1. Event Lifecycle

1.  **Creation**: An authorized user (a "host") starts an event using the `/event start` command with a valid `event_id` from `config.json`.
2.  **Activation**: The bot generates a unique 4-character alphanumeric join code and records the event as active in `active_events.json`. The host and the join code are associated with the event.
3.  **Participation**: Other users can join the event using the `/event join` command with the correct code. Their participation start time is recorded.
4.  **Termination**: The host stops the event using `/event stop`.
5.  **Point Calculation**: Upon termination, the bot calculates the participation duration for every user in the event. Points are awarded based on the `points_per_minute` defined in the event's configuration.
6.  **Data Update**: User points are updated in `points.json`, and a detailed record of each participation is appended to `event_records.json`. The event is removed from `active_events.json`.

### 3.2. Point Calculation

Points are calculated with the following formula:
`points = (duration_in_minutes * points_per_minute)`
The result is rounded to two decimal places.

## 4. Command Specification

All commands are implemented as Discord Slash Commands under the main `/event` group.

| Command           | Description                                                              | Arguments          | Permissions      |
| ----------------- | ------------------------------------------------------------------------ | ------------------ | ---------------- |
| `/event start`    | Starts a new event and generates a join code.                            | `event_id` (string)| Anyone           |
| `/event join`     | Joins an active event using its code.                                    | `code` (string)    | Anyone           |
| `/event stop`     | Stops the event hosted by the user and calculates points.                | None               | Event Host       |
| `/event kick`     | Removes a participant from the host's event.                             | `member` (User)    | Event Host       |
| `/event list`     | Lists all participants in the host's current event.                      | None               | Event Host       |
| `/event me`       | Shows the user's own total points and event history.                     | None               | Anyone           |
| `/event id`       | Lists all available event IDs and their types from `config.json`.        | None               | Anyone           |
| `/event summary`  | Displays a server-wide point leaderboard.                                | None               | Anyone           |
| `/event records`  | Displays a log of the most recent event participation records.           | None               | Administrator    |
| `/event reset`    | Backs up and clears all event data, points, and active events.           | None               | Administrator    |

## 5. Configuration Files

### 5.1. `config.json`

This file defines the types of events that can be run. It contains a list of event objects.

**Structure**:
| `/event records`  | Displays a log of the most recent event participation records.           | None               | Anyone           |
{
  "events": [
    {
      "event_id": "sfl_study",
      "event_type": "SFL Study Session",
      "points_per_minute": 0.5
    },
    {
      "event_id": "community_gaming",
      "event_type": "Community Gaming Night",
      "points_per_minute": 0.25
    }
  ]
}
```

-   `event_id`: A unique string identifier used in the `/event start` command.
-   `event_type`: A user-friendly name for the event.
-   `points_per_minute`: The number of points awarded for each minute of participation.

### 5.2. `.env`

This file stores environment variables.

**Structure**:
```
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
-   **Missing Permissions**: The administrative command (`/event reset`) will fail with an informative error if used by a non-administrator.

-   `DISCORD_TOKEN`: The bot's secret token provided by the Discord Developer Portal.

## 6. Error Handling and Edge Cases

-   **Stale PID File**: The bot checks for and removes stale `bot.pid` files on startup to recover from improper shutdowns.
-   **Concurrent Instances**: The bot will exit if it detects another instance is already running.
-   **Invalid JSON**: If a data file is corrupted or empty, the bot will initialize it with default empty data to prevent crashes.
-   **Missing Permissions**: Administrative commands (`/event reset`, `/event records`) will fail with an informative error if used by a non-administrator.
-   **User Not Found**: When generating leaderboards or lists, if a user has left the server, the bot will display their ID as a fallback.
