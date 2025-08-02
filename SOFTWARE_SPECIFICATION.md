# Software Specification: SFL Event-based Activity Points Bot

## 1. Introduction

This document outlines the software specifications for the "SFL Event-based Activity Points Bot," a Discord bot designed to automate the tracking and rewarding of member participation in server events. The system uses slash commands for all interactions and relies on a configuration file for event parameters.

## 2. Core Components

### 2.1. Bot Engine

-   **Platform**: Python 3
-   **Library**: `discord.py`
-   **Dependencies**: `python-dotenv`
-   **Authentication**: The bot authenticates with Discord's Gateway using a static token stored in a `.env` file.

### 2.2. Configuration Management

-   A `config.json` file stores the parameters for different event types.
-   Each event configuration includes:
    -   `event_id` (integer): A unique identifier for the event type.
    -   `event_type` (string): A human-readable name for the event (e.g., "Community Hangout").
    -   `points_per_minute` (float): The number of points awarded for each minute of participation.

### 2.3. Data Persistence

-   The bot stores data locally in a `data/` directory.
-   **Active Events (`active_events.json`)**: A JSON object where keys are the 4-character event codes. Each event object contains:
    -   `creator_id`: The Discord user ID of the event host.
    -   `event_id`: The ID of the event from `config.json`.
    -   `start_time`: The ISO 8601 timestamp when the event was started.
    -   `participants`: A dictionary where keys are participant user IDs and values contain their `join_time`.
-   **Points Data (`points.json`)**: A JSON object where keys are user IDs. Each user object contains:
    -   `total_points`: The cumulative total of points earned by the user.
    -   `events`: A dictionary where keys are `event_id`s and values are the total points earned for that event type.

## 3. Slash Commands (`/event`)

All commands are grouped under the `/event` prefix.

### 3.1. `/event start`

-   **Description**: Starts an event and generates a join code.
-   **Parameters**:
    -   `event_id` (string): The ID of the event to start, as defined in `config.json`.
-   **Functionality**:
    1.  Checks if the `event_id` is valid.
    2.  Checks if the user is already hosting another event. If so, returns an error.
    3.  Generates a unique 4-character alphanumeric code.
    4.  Creates a new entry in `active_events.json` with the creator as the first participant.
    5.  Responds with an ephemeral message containing the event type and the join code.

### 3.2. `/event stop`

-   **Description**: Stops the event hosted by the command user.
-   **Functionality**:
    1.  Identifies the event hosted by the user. If none, returns an error.
    2.  For each participant (including the creator), calculates the participation duration.
    3.  Calculates points based on `duration_minutes * points_per_minute`.
    4.  Updates the `points.json` file with the calculated points for each participant.
    5.  Removes the event from `active_events.json`.
    6.  Responds with a confirmation message.

### 3.3. `/event join`

-   **Description**: Allows a user to join an active event.
-   **Parameters**:
    -   `code` (string): The 4-character event code.
-   **Functionality**:
    1.  Validates the event code against `active_events.json`.
    2.  Checks if the user has already joined the event.
    3.  Adds the user's ID and `join_time` to the event's participant list.
    4.  Responds with an ephemeral confirmation message.

### 3.4. `/event kick`

-   **Description**: Removes a participant from an event.
-   **Parameters**:
    -   `member` (Member): The Discord member to remove.
-   **Functionality**:
    1.  Only the event creator can use this command.
    2.  Calculates and finalizes points for the kicked member.
    3.  Removes the member from the event's participant list in `active_events.json`.
    4.  Responds with a confirmation message.

### 3.5. `/event list`

-   **Description**: Lists all participants in the user's currently hosted event.
-   **Functionality**:
    1.  Finds the event hosted by the user.
    2.  Fetches the display names of all participants.
    3.  Displays the list in an embedded message.

### 3.6. `/event id`

-   **Description**: Lists all available event IDs and their types.
-   **Functionality**:
    1.  Reads `config.json`.
    2.  Displays a list of all configured events in the format: `event_id - event_type`.

### 3.7. `/event me`

-   **Description**: Shows a user their own point summary.
-   **Functionality**:
    1.  Retrieves the user's data from `points.json`.
    2.  Displays an embed showing:
        -   A breakdown of points earned per event type.
        -   The user's total accumulated points.

### 3.8. `/event summary`

-   **Description**: Displays a server-wide point leaderboard.
-   **Functionality**:
    1.  Reads `points.json`.
    2.  Sorts all users by `total_points` in descending order.
    3.  Displays a ranked list showing each member's display name and their total points.

### 3.9. `/event records`

-   **Description**: Shows the detailed point records for a specific member.
-   **Parameters**:
    -   `member` (Member): The member whose records are to be viewed.
-   **Functionality**:
    1.  Retrieves the specified member's data from `points.json`.
    2.  Displays an embed showing a breakdown of points earned for each event type.

### 3.10. `/event reset`

-   **Description**: Clears all event and point data.
-   **Permissions**: Administrator only.
-   **Functionality**:
    1.  Clears all data from `active_events.json` and `points.json`.
    2.  Resets the corresponding in-memory variables.
    3.  Responds with a confirmation message.

## 4. Error Handling

-   **Invalid Commands/Parameters**: The bot provides ephemeral error messages for invalid inputs (e.g., wrong event ID, invalid join code).
-   **Permissions**: The `/event reset` command is restricted to users with Administrator permissions.
-   **File I/O**: The bot includes error handling for reading from and writing to data files.
-   **Missing Configuration**: The bot will log a fatal error and exit if `config.json` is missing or invalid.
-   **Missing Token**: The bot will log a fatal error and exit if the `DISCORD_TOKEN` is not found in the `.env` file.
