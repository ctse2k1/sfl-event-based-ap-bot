# Software Specification: SFL Event-Based Activity Point Bot

## 1. Introduction

### 1.1. Purpose
This document outlines the software specifications for the SFL Event-Based Activity Point Bot. The bot is designed to automate the tracking of user participation in Discord voice channel events and reward them with activity points. This system aims to increase community engagement by providing a transparent and automated incentive system.

### 1.2. Scope
The bot will operate within a Discord server environment. Its primary functions include starting and stopping events, tracking user time in voice channels during events, calculating points, and providing users and administrators with access to participation data.

### 1.3. Definitions, Acronyms, and Abbreviations
- **Discord:** A VoIP and instant messaging social platform.
- **Bot:** An automated program that runs on Discord.
- **Guild:** A Discord server.
- **Voice Channel (VC):** A channel on a Discord server where users can communicate via voice and video.
- **Event:** A time-bound activity occurring in a specific voice channel, managed by the bot.
- **Event Manager:** A user with a specific role that grants them permission to manage bot events.
- **Activity Points (AP):** Points awarded to users for their participation in events.
- **JSON:** JavaScript Object Notation, a lightweight data-interchange format.

## 2. System Architecture

### 2.1. High-Level Architecture
The system is a single Python application that connects to the Discord Gateway API via the `discord.py` library. It maintains its state and data in-memory, with periodic persistence to local JSON files.

- **Core Logic:** `bot.py` contains the main application logic, including command handling, event tracking, and point calculation.
- **Configuration:** `config.json` stores the definitions of event types and their point values.
- **Data Storage:**
    - `active_events.json`: Stores the state of currently running events.
    - `event_records.json`: A persistent log of all user participation records from completed events.
- **Environment Variables:** A `.env` file stores sensitive information, primarily the `DISCORD_TOKEN`.

### 2.2. Dependencies
- **`discord.py`**: The primary library for interacting with the Discord API.
- **`python-dotenv`**: For managing environment variables.
- **Standard Python Libraries:** `json`, `os`, `datetime`, `asyncio`, `logging`.

## 3. Functional Requirements

### 3.1. Event Management
- **FR1.1: Start Event:** An authorized user (Event Manager) must be able to start an event by specifying an `event_id`. The event is tied to the voice channel the manager is currently in.
- **FR1.2: Stop Event:** An authorized user must be able to stop an active event using its `event_id`. Upon stopping, the bot will finalize points for all participants.
- **FR1.3: Unique Events:** The bot must prevent starting an event that is already active.
- **FR1.4: Authorization:** Access to start and stop commands shall be restricted to users with the "Event Manager" role.

### 3.2. Point Calculation and Tracking
- **FR2.1: Participant Tracking:** The bot must track all users present in the designated voice channel from the moment an event starts.
- **FR2.2: Time Calculation:** The bot shall calculate the total duration (in minutes) that each user spent in the voice channel during the event.
- **FR2.3: Point Awarding:** Points will be calculated by multiplying the user's participation duration by the `points_per_minute` value defined in `config.json` for that event type.
- **FR2.4: Data Recording:** For each participant in a completed event, a record shall be created containing `user_id`, `event_id`, `event_type`, `start_time`, `end_time`, `duration_minutes`, and `points_earned`.

### 3.3. Data Persistence
- **FR3.1: Active Events:** The state of all active events must be saved to `active_events.json` to allow recovery from bot restarts.
- **FR3.2: Participation Records:** All finalized participation records must be appended to `event_records.json`. This file serves as the master database for all user activity.

### 3.4. User-Facing Commands
- **FR4.1: Personal Stats (`/event me`):** Any user must be able to view their own total accumulated points and a history of their event participation.
- **FR4.2: Leaderboard (`/event summary`):** Any user must be able to view a server-wide leaderboard that ranks users by total points.
- **FR4.3: Event List (`/event id`):** Any user must be able to list all configured event types and their corresponding IDs.
- **FR4.4: Active Participants (`/event participants`):** Any user must be able to see the list of participants currently in an active event.

### 3.5. Administrative Commands
- **FR5.1: Data Export (`/event export`):** An Event Manager must be able to export the `event_records.json` file.
- **FR5.2: Bot Termination (`/bot terminate`):** The bot owner (as defined by Discord API) must be able to shut down the bot gracefully.

## 4. Non-Functional Requirements

### 4.1. Usability
- **NFR1.1:** Commands should be implemented as Discord slash commands for ease of use.
- **NFR1.2:** Responses to commands should be clear, concise, and formatted using Discord embeds for better readability.
- **NFR1.3:** Error messages should be user-friendly and provide guidance on how to correct the issue.

### 4.2. Reliability
- **NFR2.1:** The bot should handle unexpected disconnects from Discord and attempt to reconnect automatically.
- **NFR2.2:** The bot should gracefully handle cases where a user leaves the server or cannot be fetched, logging an appropriate message instead of crashing.
- **NFR2.3:** Data integrity must be maintained. JSON files should be written atomically where possible to prevent corruption.

### 4.3. Performance
- **NFR3.1:** Command responses should be delivered within 3 seconds under normal load. For potentially long-running tasks (like generating a large summary), the bot should use deferred responses.

### 4.4. Configurability
- **NFR4.1:** Event types and point values must be configurable through the `config.json` file without requiring code changes.

### 4.5. Security
- **NFR5.1:** The bot's Discord token must be stored securely and not be hardcoded in the source code.
- **NFR5.2:** Command access must be strictly enforced based on user roles.

## 5. Data Model

### 5.1. `config.json`
A dictionary where keys are `event_id` (stringified integer).
```json
{
  "event_id": {
    "event_type": "string",
    "points_per_minute": "float"
  }
}
```

### 5.2. `active_events.json`
A dictionary where keys are `event_id`.
```json
{
  "event_id": {
    "start_time": "ISO 8601 string",
    "vc_id": "integer",
    "manager_id": "integer",
    "participants": {
      "user_id": {
        "start_time": "ISO 8601 string"
      }
    }
  }
}
```

### 5.3. `event_records.json`
A list of participation record objects.
```json
[
  {
    "user_id": "string",
    "event_id": "string",
    "event_type": "string",
    "start_time": "ISO 8601 string",
    "end_time": "ISO 8601 string",
    "duration_minutes": "float",
    "points_earned": "float"
  }
]
```
