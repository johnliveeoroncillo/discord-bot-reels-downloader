# Facebook Reels Downloader & Discord Bot

A Python script to download Facebook Reels videos as MP4 files, with an optional Discord bot that can automatically convert and post Facebook Reels links in a specified channel.

## Prerequisites

- Python 3.6 or higher
- pip (Python package installer)
- FFmpeg (for handling video conversion)

## Installation

1. Clone this repository or download the script
2. Install the required dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

3. The script will automatically download and set up a static FFmpeg binary in the project's `bin` directory when you first run it.

## Discord Bot Setup

1. Create a new Discord bot:
   - Go to the [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application" and give it a name
   - Go to the "Bot" tab and click "Add Bot"
   - Under "Privileged Gateway Intents", enable "Message Content Intent"
   - Copy the bot token (click "Copy" under the bot's username)

2. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file and add your bot token and channel ID.

3. Get your channel ID:
   - In Discord, enable Developer Mode (User Settings > Advanced > Developer Mode)
   - Right-click on the channel where you want the bot to operate and select "Copy ID"
   - Paste this ID as the `CHANNEL_ID` in your `.env` file

4. Invite the bot to your server:
   - Go to the OAuth2 > URL Generator in the Discord Developer Portal
   - Select `bot` and `applications.commands` scopes
   - Select these permissions: `Read Messages/View Channels`, `Send Messages`, `Manage Messages`, `Attach Files`
   - Copy the generated URL and open it in your browser to add the bot to your server

## Docker Setup

1. Make sure you have Docker and Docker Compose installed on your system.

2. Create a `.env` file if you haven't already:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file and add your Discord bot token and channel ID.

3. Build and start the container:
   ```bash
   docker-compose up --build -d
   ```

4. To view logs:
   ```bash
   docker logs -f fbreels-bot
   ```

5. To stop the container:
   ```bash
   docker-compose down
   ```

### Local Development

If you prefer to run the bot without Docker, follow these steps:

1. Install Python 3.6 or higher
2. Install the required dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```
3. Run the bot:
   ```bash
   python3 bot.py
   ```

## Usage

### Command Line

```bash
python3 main.py "https://www.facebook.com/reel/VIDEO_ID/"
```

Replace `VIDEO_ID` with the actual Facebook Reel ID from the URL.

### Discord Bot

1. Start the bot:
   ```bash
   python3 discord_bot.py
   ```

2. The bot will now listen for Facebook Reels links in the specified channel.
3. When a user posts a Facebook Reels link, the bot will:
   - Download the video
   - Delete the original message (to keep the chat clean)
   - Post the video with the original message text (if any)

## How It Works

The script uses `yt-dlp` to download the video in the best available quality and saves it as an MP4 file in a `downloads` directory.

## Notes

- The script creates a `downloads` directory in the same folder where it's run
- Videos are saved with their original titles from Facebook
- Make sure you have the necessary permissions to download the content
