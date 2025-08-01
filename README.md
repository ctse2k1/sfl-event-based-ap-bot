# SFL Event-based Activity Points Bot

A simple yet powerful Discord bot designed to automate the tracking of activity points for members participating in server events. It uses slash commands to provide a fair, engaging, and transparent system for rewarding user participation.

## Features
- **Event Management:** Start, stop, and manage events with simple commands.
- **Automated Point Calculation:** Automatically calculates points based on participation time.
- **Persistent Data:** Stores user points in JSON files, ensuring data survives bot restarts.
- **Easy Participation:** Members can join events with a unique, temporary 4-character code.
- **Leaderboards:** View detailed records and a summary of total points for all users.
- **Slash Command Integration:** All features are accessible via an intuitive `/event` command group.

## Prerequisites
- Python 3.8 or higher
- A Discord Application and Bot Token

## Installation & Setup

Follow these steps to get the bot running on your own server.

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/ctse2k1/sfl-event-based-ap-bot.git
    cd sfl-event-based-ap-bot
    ```

2.  **Install Dependencies**
    Install the required Python libraries using pip.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure the Environment**
    Create a file named `.env` in the root directory. This file will store your secret bot token.
    ```
    DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN_HERE
    ```
    **Important:** You must enable **Privileged Gateway Intents** for your bot in the [Discord Developer Portal](https://discord.com/developers/applications). Specifically, the **Server Members Intent** and **Message Content Intent** are required.

4.  **Set Up Configuration**
    Modify the `config.json` file to set your desired points-per-minute rate. The other fields are placeholders.
    ```json
    {
      "event_id": "sample_id",
      "event_type": "sample_type",
      "points_per_minute": 10
    }
    ```

5.  **Run the Bot**
    Execute the main script to bring your bot online.
    ```bash
    python3 bot.py
    ```

## Usage (Slash Commands)

All bot functionality is accessed through the `/event` slash command group.

### Event Creator Commands
-   ` /event start <event_id> `
    -   Starts a new event and generates a unique join code.
    -   *Constraint:* The creator cannot host more than one event at a time.

-   ` /event stop `
    -   Stops the event you are currently hosting.
    -   Calculates points for all remaining participants and saves the data.

-   ` /event kick <member> `
    -   Forcibly removes a participant from your event and calculates their points up to that moment.

-   ` /event list `
    -   Shows a list of all members currently participating in your active event.

### Participant Commands
-   ` /event join <join_code> `
    -   Allows you to join an active event using its unique 4-character code.

### General Commands
-   ` /event records `
    -   Displays a detailed, chronological log of all points awarded across all events and users.

-   ` /event summary `
    -   Shows a leaderboard of total points accumulated by each user, ranked from highest to lowest.

-   ` /event me `
    -   Shows your personal event history, the points you earned for each, and your total accumulated points.

-   ` /event reset `
    -   **[DANGEROUS]** Clears all stored event data and user points. This action is irreversible. It is recommended to restrict this command to administrators in a future update.
