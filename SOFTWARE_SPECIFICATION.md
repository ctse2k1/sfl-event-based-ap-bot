# Software Specification: SFL Event-Based Activity Point Bot

## 1. Introduction

### 1.1. Purpose
This document outlines the software specifications for the SFL Event-Based Activity Point Bot. The bot is designed to automate the tracking of user participation in timed Discord events and reward them with activity points. This system aims to increase community engagement by providing a transparent, code-based event participation system with automated point calculation and comprehensive tracking.

### 1.2. Scope
The bot operates within Discord server environments using slash commands. Its primary functions include creating events with unique join codes, managing participant registration, tracking participation duration, calculating points, and providing comprehensive data access to users and administrators.

### 1.3. Definitions, Acronyms, and Abbreviations
- **Discord:** A VoIP and instant messaging social platform
- **Bot:** An automated program that runs on Discord
- **Guild:** A Discord server
- **Event:** A time-bound activity with a unique join code, managed by the bot
- **Event Host:** A user who creates and manages an event
- **Event Code:** A unique 4-character alphanumeric identifier for joining events
- **Activity Points (AP):** Points awarded to users based on participation duration
- **JSON:** JavaScript Object Notation, a lightweight data-interchange format
- **Instance Management:** System for preventing multiple bot instances from running simultaneously

## 2. System Architecture

### 2.1. High-Level Architecture
The system is a single Python application that connects to the Discord Gateway API via the `discord.py` library. It maintains state in-memory with persistent storage to organized JSON files in a dedicated data directory.

**Core Components:**
- **Core Logic:** `bot.py` contains the main application logic, including command handling, event management, point calculation, and instance management
- **Configuration:** `config.json` stores event type definitions in an array structure
- **Data Storage Directory:** `data/` directory containing:
  - `active_events.json`: Current running events and participant data
  - `event_records.json`: Historical participation records
  - `event_records_backup_*.json`: Timestamped backups created during resets
- **Environment Variables:** `.env` file stores sensitive configuration (Discord token)

### 2.2. Dependencies
- **`discord.py`**: Primary library for Discord API interaction
- **`python-dotenv`**: Environment variable management
- **`psutil`**: Process management for instance control
- **Standard Python Libraries:** `json`, `os`, `datetime`, `asyncio`, `logging`, `random`, `string`, `time`, `sys`, `signal`, `shutil`, `atexit`

## 3. Functional Requirements

### 3.1. Instance Management
- **FR1.1: Single Instance:** The system must ensure only one bot instance runs at a time
- **FR1.2: Instance Detection:** The bot must detect other running instances using process inspection
- **FR1.3: Graceful Termination:** Duplicate instances must be terminated gracefully with SIGTERM, followed by SIGKILL if necessary
- **FR1.4: Startup Logging:** Instance management activities must be logged for monitoring

### 3.2. Event Management
- **FR2.1: Start Event:** Event hosts must be able to start events by specifying a valid `event_id`
- **FR2.2: Unique Codes:** Each event must generate a unique 4-character alphanumeric join code
- **FR2.3: Host Limitation:** Users can only host one event at a time
- **FR2.4: Stop Event:** Event hosts must be able to stop their active events, triggering point finalization
- **FR2.5: Join Event:** Any user can join active events using valid join codes
- **FR2.6: Duplicate Prevention:** Users cannot join the same event multiple times
- **FR2.7: Participant Management:** Event hosts can remove participants and list current participants
- **FR2.8: Auto-Registration:** Event creators are automatically registered as participants

### 3.3. Point Calculation and Tracking
- **FR3.1: Time Tracking:** The system must track participation duration from join time to leave/kick time
- **FR3.2: Point Calculation:** Points = participation_duration_minutes × event_points_per_minute
- **FR3.3: Precision:** Duration and points must be calculated with 2-decimal precision
- **FR3.4: Minimum Points:** Point calculations must not result in negative values
- **FR3.5: Real-time Calculation:** Points are calculated immediately when participants leave or are kicked

### 3.4. Data Persistence and Structure
- **FR4.1: Data Directory:** All data files must be stored in a dedicated `data/` directory
- **FR4.2: Active Events Storage:** Current event states must persist in `data/active_events.json`
- **FR4.3: Historical Records:** Completed participation records must be stored in `data/event_records.json`
- **FR4.4: Record Structure:** Each record must contain: user_id, event_id, event_type, start_time, end_time, duration_minutes, points_earned
- **FR4.5: Automatic Backup:** Reset operations must create timestamped backups before data deletion

### 3.5. User Interface Commands
- **FR5.1: Personal Statistics (`/event me`):** Users must be able to view their participation history and total points with rich embed formatting
- **FR5.2: Server Leaderboard (`/event summary`):** Display server-wide point rankings with user-friendly formatting
- **FR5.3: Event Types (`/event id`):** List all available event types and their identifiers
- **FR5.4: Global Records (`/event records`):** Display recent participation records across all users (limited to 20 most recent)
- **FR5.5: Participant List (`/event list`):** Event hosts can view current participants in their events

### 3.6. Administrative Functions
- **FR6.1: Data Reset (`/event reset`):** Administrators can clear all event data with automatic backup creation
- **FR6.2: Permission Control:** Reset functionality must be restricted to users with Administrator permissions
- **FR6.3: Error Handling:** Administrative commands must provide clear error messages for permission failures
- **FR6.4: Backup Naming:** Backups must use timestamp format: `event_records_backup_YYYYMMDD_HHMMSS.json`

### 3.7. Configuration Management
- **FR7.1: Array Structure:** Configuration must support an array of event objects
- **FR7.2: Event Definition:** Each event must specify event_id, event_type, and points_per_minute
- **FR7.3: Validation:** Invalid event IDs must be rejected with appropriate error messages
- **FR7.4: Runtime Loading:** Configuration must be loaded at startup with error handling for missing/invalid files

## 4. Non-Functional Requirements

### 4.1. Performance
- **NFR1.1: Response Time:** The bot must respond to commands within 3 seconds under normal conditions
- **NFR1.2: Concurrent Events:** The system must handle at least 10 concurrent events without performance degradation
- **NFR1.3: Data Processing:** Point calculations and data persistence operations must complete within 1 second
- **NFR1.4: Memory Management:** The bot must efficiently manage memory usage for large participation datasets

### 4.2. Reliability
- **NFR2.1: Uptime:** The bot should maintain 99.5% uptime during operational periods
- **NFR2.2: Auto-Recovery:** The bot must gracefully handle Discord API disconnections with automatic reconnection
- **NFR2.3: State Recovery:** Active events must be restored from persistent storage after unexpected restarts
- **NFR2.4: Data Integrity:** All participation records must be accurately preserved across system restarts
- **NFR2.5: Error Resilience:** The system must continue operating despite individual command failures

### 4.3. Usability
- **NFR3.1: User Interface:** All command responses must use rich Discord embeds for improved readability
- **NFR3.2: Error Messages:** Error messages must be clear, specific, and provide actionable guidance
- **NFR3.3: Command Discovery:** All commands must be discoverable through Discord's slash command interface
- **NFR3.4: Feedback:** Users must receive immediate confirmation for all successful operations
- **NFR3.5: Data Presentation:** Leaderboards and statistics must be formatted for easy comprehension

### 4.4. Security
- **NFR4.1: Token Security:** Discord bot tokens must be stored in environment variables, never in source code
- **NFR4.2: Permission Control:** Administrative functions must verify Discord server permissions
- **NFR4.3: Data Privacy:** User data must be stored locally and not transmitted to external services
- **NFR4.4: Input Validation:** All user inputs must be validated to prevent injection attacks

### 4.5. Maintainability
- **NFR5.1: Code Structure:** Code must be modular with clear separation of concerns
- **NFR5.2: Logging:** All significant operations must be logged with appropriate detail levels
- **NFR5.3: Configuration:** Event types must be configurable without code modifications
- **NFR5.4: Documentation:** Code must include inline documentation for complex operations

### 4.6. Scalability
- **NFR6.1: Data Growth:** The system must handle growing participation datasets efficiently
- **NFR6.2: User Base:** The bot must support Discord servers with up to 1000 active participants
- **NFR6.3: Event History:** Historical data must remain accessible as the dataset grows
- **NFR6.4: Backup Management:** Backup files must be managed to prevent excessive disk usage

## 5. Data Structures

### 5.1. Configuration Structure (`config.json`)
```json
{
  "events": [
    {
      "event_id": "string",
      "event_type": "string", 
      "points_per_minute": number
    }
  ]
}
```

### 5.2. Active Events Structure (`data/active_events.json`)
```json
{
  "event_code": {
    "creator_id": "string",
    "event_id": "string",
    "start_time": "ISO8601_timestamp",
    "participants": {
      "user_id": {
        "join_time": "ISO8601_timestamp"
      }
    }
  }
}
```

### 5.3. Event Records Structure (`data/event_records.json`)
```json
[
  {
    "user_id": "string",
    "event_id": "string", 
    "event_type": "string",
    "start_time": "ISO8601_timestamp",
    "end_time": "ISO8601_timestamp",
    "duration_minutes": number,
    "points_earned": number
  }
]
```

## 6. Error Handling

### 6.1. Configuration Errors
- **Missing config.json:** Application must exit with clear error message
- **Invalid JSON format:** Application must exit with parsing error details
- **Missing required fields:** Application must validate and report specific missing fields

### 6.2. Runtime Errors
- **Discord API failures:** Commands must provide user-friendly error messages
- **File I/O errors:** Data operations must handle file access failures gracefully
- **Invalid user inputs:** Commands must validate inputs and provide specific error feedback
- **Permission errors:** Administrative commands must clearly indicate permission requirements

### 6.3. Data Consistency
- **Corrupted data files:** System must detect and handle corrupted JSON files
- **Missing participants:** Point calculations must handle missing participant data
- **Invalid timestamps:** Date parsing must handle malformed timestamp data

## 7. Deployment Requirements

### 7.1. Environment Setup
- **Python Version:** Python 3.8 or higher required
- **Dependencies:** All dependencies must be installable via pip from requirements.txt
- **Directory Structure:** Bot must create required directories automatically
- **Environment Variables:** .env file must be present with valid DISCORD_TOKEN

### 7.2. Runtime Requirements
- **Disk Space:** Minimum 100MB for data storage and logs
- **Memory:** Minimum 256MB RAM for normal operation
- **Network:** Stable internet connection for Discord API access
- **Permissions:** File system write permissions for data directory
