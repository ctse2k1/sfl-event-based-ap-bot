# Software Specification: SFL Event-Based Activity Point Bot

## 1. Introduction

This document outlines the software specification for the SFL Event-Based Activity Point Bot. The bot is a Python-based application designed to run on a Discord server, allowing event hosts to track participation and automatically award points to members based on their active time in an event.

## 2. System Overview

The system is a Discord bot built using the `discord.py` library. It operates using slash commands and persists data to the local filesystem in JSON format. The bot is designed to be stateful, meaning it remembers active events and user points across restarts.

### 2.1. Core Components

-   **Bot (`bot.py`)**: The main application logic. It handles Discord API interaction, command processing, and data management.
-   **Configuration (`config.json`)**: A user-defined JSON file that specifies the types of events that can be run and their corresponding point values.
-   **Data Persistence Layer**: A set of helper functions that read from and write to JSON files in the `data/` directory. This includes active events, user point totals, and historical event records.
-   **PID Lock**: A mechanism to ensure only one instance of the bot is running at any given time by creating a `bot.pid` file.

## 3. Functional Requirements

### 3.1. Event Management

-   **FR1.1 - Start Event**: A user must be able to start an event by providing a valid `event_id` from `config.json`. The system shall generate a unique, 4-character alphanumeric join code. A user cannot host more than one event at a time.
-   **FR1.2 - Stop Event**: The event creator must be able to stop their event. Upon stopping, the system will calculate points for all participants and clear the event from the active list.
-   **FR1.3 - Join Event**: Any server member must be able to join an active event using its specific join code.
-   **FR1.4 - Kick Participant**: The event creator must be able to remove a participant from their event. The kicked user's points will be calculated and saved up to the point of removal.
-   **FR1.5 - List Participants**: The event creator must be able to view a list of all current participants in their event.

### 3.2. Point Calculation

-   **FR2.1 - Time-Based Accrual**: Points shall be calculated based on the duration a participant is in an event (from join time to event stop/kick time).
-   **FR2.2 - Configurable Rate**: The rate of point accrual (points per minute) must be configurable for each event type in `config.json`.
-   **FR2.3 - Finalization**: Points are calculated and awarded only when an event stops or a user is kicked.

### 3.3. Data & Display

-   **FR3.1 - Personal Points (`/event me`)**: A user must be able to view their own total points and a breakdown of points earned per event type.
-   **FR3.2 - Server Leaderboard (`/event summary`)**: The bot must provide a server-wide leaderboard, showing the top users ranked by total points.
-   **FR3.3 - Event IDs (`/event id`)**: The bot must display a list of all available event types and their corresponding IDs from the configuration file.
-   **FR3.4 - Event Records (`/event records`)**: The bot must display a historical log of all participation records, including user, event type, duration, and points earned.

### 3.4. Administrative Functions

-   **FR4.1 - Data Reset (`/event reset`)**: An administrator must have the ability to clear all active events, points, and records.
-   **FR4.2 - Data Backup**: Before executing a reset, the system must create a timestamped backup of the `event_records.json` file.
-   **FR4.3 - Permissions**: The reset command must be restricted to users with Administrator permissions on the server.

## 4. Non-Functional Requirements

-   **NFR1 - Persistence**: All event data, points, and records must be stored on the local filesystem and survive bot restarts.
-   **NFR2 - Usability**: Interaction with the bot must be handled through intuitive Discord slash commands. Responses should be clear and often ephemeral to avoid cluttering chat channels.
-   **NFR3 - Error Handling**: The bot must gracefully handle invalid inputs, such as incorrect event codes or non-existent event IDs.
-   **NFR4 - Concurrency**: The system must prevent more than one instance of the bot from running at the same time using a PID lock file.

## 5. Data Structures

### 5.1. `active_events.json`

A dictionary where keys are event join codes.

```json
{
  "abcd": {
    "creator_id": "123456789012345678",
    "event_id": "1",
    "start_time": "2023-10-27T10:00:00.000000+00:00",
    "participants": {
      "123456789012345678": { "join_time": "2023-10-27T10:00:00.000000+00:00" },
      "876543210987654321": { "join_time": "2023-10-27T10:05:00.000000+00:00" }
    }
  }
}
```

### 5.2. `points.json`

A dictionary where keys are user IDs.

```json
{
  "123456789012345678": {
    "total_points": 50.5,
    "events": {
      "1": 20.5,
      "2": 30.0
    }
  }
}
```

### 5.3. `event_records.json`

A list of record objects.

```json
[
  {
    "user_id": "123456789012345678",
    "event_id": "1",
    "event_type": "Community Hangout",
    "start_time": "2023-10-27T10:00:00.000000+00:00",
    "end_time": "2023-10-27T11:00:00.000000+00:00",
    "duration_minutes": 60.0,
    "points_earned": 30.0
  }
]
```
