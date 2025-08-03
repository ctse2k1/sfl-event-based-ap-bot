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
- **Event Host:** A user who starts an event.
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
- **FR1.1: Start Event:** An event host must be able to start an event by specifying an `event_id`.
- **FR1.2: Stop Event:** An event host must be able to stop an active event. Upon stopping, the bot will finalize points for all participants.
- **FR1.3: Join Event:** Any user can join an active event using a 4-character code.
- **FR1.4: Kick from Event:** The event host can remove a participant from the event.
- **FR1.5: List Participants:** The event host can list all participants in their event.

### 3.2. Point Calculation and Tracking
- **FR2.1: Participant Tracking:** The bot must track all users who have joined an event.
- **FR2.2: Time Calculation:** The bot shall calculate the total duration (in minutes) that each user participated in the event.
- **FR2.3: Point Awarding:** Points will be calculated by multiplying the user's participation duration by the `points_per_minute` value defined in `config.json` for that event type.
- **FR2.4: Data Recording:** For each participant in a completed event, a record shall be created containing `user_id`, `event_id`, `event_type`, `start_time`, `end_time`, `duration_minutes`, and `points_earned`.

### 3.3. Data Persistence
- **FR3.1: Active Events:** The state of all active events must be saved to `active_events.json` to allow recovery from bot restarts.
- **FR3.2: Participation Records:** All finalized participation records must be saved to `event_records.json`.

### 3.4. User-Facing Commands
- **FR4.1: Me Command:** A user must be able to view their own total points and event history.
- **FR4.2: Summary Command:** Any user must be able to view a server-wide leaderboard of points.
- **FR4.3: ID Command:** Any user must be able to list all available event types and their IDs.

### 3.5. Bot Administration
- **FR5.1: Terminate:** The bot owner must be able to shut down the bot gracefully.
