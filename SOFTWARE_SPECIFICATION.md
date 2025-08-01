# Software Specification: SFL Event-based Activity Points Bot

## 1. Introduction

### 1.1. Project Name
sfl-event-based-ap-bot

### 1.2. Purpose
This document outlines the software specifications for a Discord bot designed to automate the calculation and tracking of activity points for members participating in server events. The bot aims to provide a fair, engaging, and transparent system for rewarding user participation during organized activities.

## 2. System Overview

### 2.1. Architecture
The system is a monolithic Discord bot application. It runs as a single Python script that connects to the Discord Gateway API. It listens for slash command interactions from users and manages event and user data through a combination of in-memory dictionaries (for active sessions) and persistent JSON files (for long-term point storage).

### 2.2. Technologies
- **Programming Language:** Python 3
- **Core Library:** `discord.py` for Discord API interaction and command handling.
- **Configuration:** `python-dotenv` for secure management of the bot token via environment variables.
- **Data Persistence:** JSON files located in the `data/` directory for storing user point records.

## 3. Functional Requirements (Slash Commands)

The bot's entire functionality is exposed through a primary slash command group: `/event`.

### 3.1. `/event start`
- **Description:** Initiates a new event, making it available for members to join.
- **Actor:** Event Creator (any member with permissions to use slash commands).
- **Preconditions:** The creator must not be currently hosting another active event.
- **Input:** `event_id` (String): A user-defined identifier for the event.
- **Process:**
  1. The bot checks if the creator is already hosting an event. If so, it returns an ephemeral error message.
  2. A unique 4-character join code is generated for the session.
  3. A new event session is created in-memory, storing the creator's ID, the event ID, the start time, and the unique join code.
  4. The creator is automatically added as the first participant in the event.
  5. The bot responds with an ephemeral message containing the event ID and the join code.
- **Output:** "Event started with ID: `{event_id}`. Join code: `{join_code}`"

### 3.2. `/event join`
- **Description:** Allows a member to join an active event.
- **Actor:** Participant.
- **Input:** `join_code` (String): The 4-character code for the event.
- **Process:**
  1. The bot validates the join code against all active events. If the code is invalid, it returns an error.
  2. The bot checks if the participant has already joined the event. If so, it returns an error.
  3. The participant is added to the event's participant list with their join timestamp.
- **Output:** "You have successfully joined the event: `{event_id}`."

### 3.3. `/event stop`
- **Description:** Ends an event, calculates points for all remaining participants, and saves the data.
- **Actor:** Event Creator.
- **Preconditions:** The creator must be the host of an active event.
- **Process:**
  1. The bot verifies that the command user is the creator of an active event.
  2. For the creator and each participant still in the session, the bot calculates the total participation duration.
  3. Points are calculated based on the duration and the `points_per_minute` value from `config.json`.
  4. The calculated points are appended to the persistent user records in `data/user_points.json`.
  5. The active event session is terminated and removed from memory.
- **Output:** "Event `{event_id}` has been stopped. Points have been calculated and awarded."

### 3.4. `/event kick`
- **Description:** Forcibly removes a participant from an active event and calculates their points up to that moment.
- **Actor:** Event Creator.
- **Input:** `member` (Discord Member): The user to be removed.
- **Process:**
  1. The bot verifies the command user is the creator of an active event.
  2. The bot checks if the target member is a participant in that event.
  3. Points are calculated for the kicked member based on their participation duration.
  4. The points are saved to persistent storage.
  5. The member is removed from the active event's participant list.
- **Output:** "`{member_name}` has been kicked from the event. Their points have been calculated."

### 3.5. `/event list`
- **Description:** Lists all current participants in the creator's active event.
- **Actor:** Event Creator.
- **Process:**
  1. The bot verifies the command user is the creator of an active event.
  2. It retrieves the list of participants for that event.
  3. It formats and displays the list of participant names in a Discord embed.
- **Output:** An embed listing the active participants.

### 3.6. `/event records`
- **Description:** Displays a detailed, chronological log of all points awarded across all events.
- **Actor:** Any member.
- **Process:**
  1. The bot reads the `data/user_points.json` file.
  2. It formats the data into a readable list, showing User, Event ID, and Points Awarded for each entry.
- **Output:** An embed with a detailed breakdown of all point records.

### 3.7. `/event summary`
- **Description:** Displays a summary of total points accumulated by each user, ranked highest to lowest.
- **Actor:** Any member.
- **Process:**
  1. The bot reads `data/user_points.json`.
  2. It aggregates the points for each user across all events.
  3. It displays a leaderboard-style summary.
- **Output:** An embed summarizing total points per user.

### 3.8. `/event reset`
- **Description:** Clears all stored event data and user points. This is a destructive action.
- **Actor:** Any member (Note: Should be restricted to administrators in a future update).
- **Process:**
  1. The bot clears the in-memory `active_events` dictionary.
  2. The bot deletes or clears the `data/user_points.json` file.
- **Output:** "All event data and user points have been reset."

### 3.9. `/event me`
- **Description:** Allows a user to view their own accumulated points and event history.
- **Actor:** Any member.
- **Process:**
  1. The bot reads `data/user_points.json`.
  2. It filters the records for the command user.
  3. It displays a list of events the user participated in, the points for each, and their total accumulated points.
- **Output:** An embed detailing the user's personal point history and total.

## 4. Non-Functional Requirements

- **4.1. Usability:** The bot must be user-friendly, with clear and concise command descriptions and responses. All interactions are via Discord's native slash command interface.
- **4.2. Reliability:** The bot handles common user errors gracefully (e.g., joining an event twice, stopping an event that doesn't exist). Data persistence ensures that points are not lost if the bot restarts unexpectedly.
- **4.3. Performance:** Command responses should feel near-instantaneous (under 3 seconds). The current design is suitable for small to medium-sized servers.

## 5. Data Management

### 5.1. Active Event Data (Volatile)
- **Storage:** A Python dictionary (`active_events`) held in-memory. This data is lost on bot shutdown.
- **Structure:**
  ```json
  {
    "creator_id": {
      "event_id": "...",
      "join_code": "...",
      "start_time": "...",
      "participants": {
        "participant_id": "join_time"
      }
    }
  }
  ```

### 5.2. Persistent Point Data
- **Storage:** A JSON file located at `data/user_points.json`.
- **Structure:** An array of objects, where each object represents a single point-awarding transaction.
  ```json
  [
    {
      "user_id": 123,
      "user_name": "Username",
      "event_id": "event_name",
      "points": 50
    }
  ]
  ```

## 6. Configuration

### 6.1. `config.json`
- **Purpose:** Contains parameters for point calculation logic.
- **Fields:**
  - `event_id`: A default or sample event identifier.
  - `event_type`: A category for the event (currently for informational purposes).
  - `points_per_minute`: The number of points awarded for each full minute of participation.

### 6.2. `.env`
- **Purpose:** Contains sensitive credentials required for bot operation.
- **Fields:**
  - `DISCORD_TOKEN`: The bot's unique token for authenticating with the Discord API.

## 7. Error Handling
The bot provides user-facing, ephemeral error messages for invalid actions, including but not limited to:
- Starting an event while another is already active.
- Joining with an invalid code or when already in an event.
- Using a creator-only command (`/event stop`, `/event kick`, `/event list`) as a non-creator.
- Requesting data (`/event me`, `/event list`) when no relevant data exists.

## 8. Future Enhancements
- Role-based permissions for commands (e.g., restricting `/event reset` to administrators).
- Support for multiple, concurrent events hosted by different creators.
- Database integration (e.g., SQLite, PostgreSQL) to replace JSON files for better scalability and data integrity.
- More complex point calculation logic (e.g., bonuses, multipliers based on event type or roles).
- A web-based dashboard for viewing event summaries and leaderboards.
