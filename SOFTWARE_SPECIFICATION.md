# Software Specification: SFL Event-Based Activity Point Bot

## 1. Introduction

This document outlines the software specifications for the SFL Event-Based Activity Point Bot. The bot is a Discord application designed to automate the tracking of member participation in guild events and award activity points accordingly. It is built using Python with the `discord.py` library.

## 2. System Architecture

The bot operates as a single, asynchronous process running `bot.py`. It interacts with the Discord API via the `discord.py` library and maintains its state through a set of local JSON files.

### 2.1. Core Components
- **Discord Bot Client (`bot.py`)**: The main entry point and runtime process. It handles the connection to Discord, registers slash commands, and listens for events (e.g., command invocations).
- **Command Handler (`discord.py` integration)**: Manages the registration and execution of application commands (slash commands) grouped under `/event` and `/admin`.
- **Event Management Module**: A collection of functions responsible for the lifecycle of an event: starting, stopping, and managing participants.
- **Point Calculation Engine**: A module responsible for calculating points based on participation duration and event type.
- **Data Persistence Layer**: A set of utility functions for reading from and writing to the JSON data files. This ensures data integrity and persistence across bot restarts.

### 2.2. Data Storage
The bot's state is persisted in the `data/` directory using JSON files.

- **`active_events.json`**: Stores a real-time list of all currently active events. This file is critical for joining events and for data recovery if the bot restarts.
- **`points.json`**: Acts as the main database for user points. It stores the total points for each user and a breakdown by event type.
- **`event_records.json`**: A detailed log file that records every single participation session for every user, including start time, end time, duration, and points earned.
- **`bot.pid`**: A lock file containing the Process ID (PID) of the running bot instance. This prevents multiple instances from starting simultaneously, which would corrupt the data files.

## 3. Data Structures

### 3.1. `active_events.json`
A JSON object where keys are the unique 4-character join codes.

```json
{
  "JOIN_CODE": {
    "event_id": "string",
    "event_name": "string",
    "creator_id": "integer (Discord User ID)",
    "start_time": "float (Unix Timestamp)",
    "participants": {
      "USER_ID": {
        "join_time": "float (Unix Timestamp)"
      }
    }
  }
}
```

### 3.2. `points.json`
A JSON object where keys are Discord User IDs.

```json
{
  "USER_ID": {
    "total_points": "integer",
    "event_points": {
      "EVENT_TYPE_1": "integer",
      "EVENT_TYPE_2": "integer"
    }
  }
}
```

### 3.3. `event_records.json`
A JSON object where keys are Discord User IDs. Each user has a list of their participation records.

```json
{
  "USER_ID": [
    {
      "event_name": "string",
      "join_time": "float (Unix Timestamp)",
      "leave_time": "float (Unix Timestamp)",
      "duration_minutes": "integer",
      "points_earned": "integer"
    }
  ]
}
```

### 3.4. `config.json`
A configuration file defining the available event types.

```json
{
  "events": [
    {
      "id": "string (Unique identifier)",
      "name": "string (Display name)",
      "points_per_minute": "integer"
    }
  ]
}
```

## 4. Functional Requirements

### 4.1. Event Creation
- **FR1.1**: A user with appropriate permissions can start an event using the `/event start` command.
- **FR1.2**: The system must accept a valid `event_id` from `config.json`.
- **FR1.3**: Upon starting, the system shall generate a unique, 4-character, alphanumeric join code.
- **FR1.4**: The system must prevent a user from starting a new event if they are already hosting one.
- **FR1.5**: The new event must be immediately saved to `active_events.json`.

### 4.2. Event Participation
- **FR2.1**: Any user can join an active event using `/event join` with a valid join code.
- **FR2.2**: The system shall record the user's ID and their `join_time`.
- **FR2.3**: A user cannot join an event they are already in.

### 4.3. Event Finalization
- **FR3.1**: The event creator can stop their event using `/event stop`.
- **FR3.2**: Upon stopping, the system shall trigger the point calculation process for all participants.
- **FR3.3**: The event must be removed from `active_events.json`.
- **FR3.4**: A summary of the event (duration, participants, total points) shall be displayed to the creator.

### 4.4. Point Calculation Algorithm
- **FR4.1**: For each participant, the duration is calculated as (`current_time` - `join_time`).
- **FR4.2**: Points are calculated as `duration_in_minutes` * `points_per_minute` (from `config.json`).
- **FR4.3**: The calculated points are added to the user's total in `points.json`.
- **FR4.4**: A detailed entry for the participation session is added to `event_records.json`.

### 4.5. User-Facing Commands
- **FR5.1**: `/event me`: A user can view their own total points and a breakdown by event type.
- **FR5.2**: `/event summary`: Any user can view a server-wide leaderboard of the top 10 users by total points.
- **FR5.3**: `/event id`: Any user can view a list of all available event types and their IDs.
- **FR5.4**: `/event list`: The event host can view a list of current participants.
- **FR5.5**: `/event kick`: The event host can remove a participant from their event, which finalizes points for that user immediately.

### 4.6. Administrative Functions
- **FR6.1**: `/admin backup`: An administrator can create a compressed `.tar.gz` backup of the `data/` directory.
- **FR6.2**: `/admin reset_user_data`: An administrator can wipe all data for a specific user from `points.json` and `event_records.json`.
- **FR6.3**: `/admin reset_all_data`: An administrator can wipe all data for all users. This action requires a secondary confirmation step.

## 5. Non-Functional Requirements

- **NFR1 (Usability)**: All functionality shall be exposed through Discord slash commands for ease of use.
- **NFR2 (Reliability)**: The bot must persist all data to the file system to ensure no data loss upon restart.
- **NFR3 (Concurrency)**: The bot must use a PID lock file (`bot.pid`) to prevent more than one instance from running, which would lead to data corruption.
- **NFR4 (Security)**: The Discord bot token must be loaded from an environment variable (`.env` file) and not be hardcoded in the source.
- **NFR5 (Configuration)**: Event types and their point values must be configurable through the `config.json` file without requiring code changes.
