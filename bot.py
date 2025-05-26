import os
import re
import asyncio
import discord
from dotenv import load_dotenv
from main import download_reel_as_mp4
from pathlib import Path
from urllib.parse import urlparse
import sys
import os

# Add the parent directory to the path so we can import utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import get_video_path

# Load environment variables
load_dotenv()

# Discord bot setup
import ssl
import aiohttp

# Enable debug logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)

print("=== Starting bot initialization ===")

# Set up intents with all necessary permissions
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True

print(f"Bot intents: {intents}")

try:
    # Create client with error handling
    class CustomClient(discord.Client):
        async def on_error(self, event, *args, **kwargs):
            logger.error(f"Error in {event}: {sys.exc_info()}")
            raise
    
    client = CustomClient(intents=intents)
    print("Client created successfully")
    
except Exception as e:
    logger.error(f"Failed to create client: {e}")
    raise

# Global connector variable will be set in main

# Configuration
CHANNEL_ID_STR = str(os.getenv('CHANNEL_ID'))
if not CHANNEL_ID_STR:
    print("Error: CHANNEL_ID not found in .env file")
    exit(1)

print(f"Raw CHANNEL_ID from .env: '{CHANNEL_ID_STR}'")

# Remove any quotes and convert to int
try:
    CHANNEL_ID = int(CHANNEL_ID_STR.strip('"\'').strip())
    print(f"Successfully parsed CHANNEL_ID: {CHANNEL_ID}")
except ValueError as e:
    print(f"Error: Invalid CHANNEL_ID in .env file. Must be a number. Error: {e}")
    print(f"CHANNEL_ID value: '{CHANNEL_ID_STR}'")
    exit(1)
DOWNLOAD_DIR = 'downloads'

# Facebook URL patterns
FACEBOOK_URL_PATTERNS = [
    r'https?://(?:www\.)?(?:facebook\.com|fb\.watch)/reel/.*',
    r'https?://(?:www\.)?facebook\.com/.*/videos/.*',
    r'https?://(?:www\.)?facebook\.com/.*/videos/.*/.*',
    r'https?://(?:www\.)?facebook\.com/watch/\?v=.*(?:&.*)?',  # Watch URLs with optional parameters like rdid
    r'https?://(?:www\.)?facebook\.com/share/r/.*',  # Shared video links like https://www.facebook.com/share/r/1C2fk5RPaQ/
    r'https?://(?:www\.)?facebook\.com/share/v/.*',  # Shared video links like https://www.facebook.com/share/v/16Tvh9Ltti/
]

def is_facebook_video_url(url):
    """Check if the URL is a Facebook video or reel."""
    for pattern in FACEBOOK_URL_PATTERNS:
        if re.match(pattern, url):
            return True
    return False

@client.event
async def on_ready():
    print('\n--- Bot is ready ---')
    print(f'Logged in as: {client.user.name}')
    print(f'Bot ID: {client.user.id}')
    print(f'Discord.py version: {discord.__version__}')
    print(f'Connected to {len(client.guilds)} guild(s):')
    for guild in client.guilds:
        print(f' - {guild.name} (ID: {guild.id})')
        print(f'   - Bot permissions: {guild.me.guild_permissions}')
        print(f'   - Bot roles: {[role.name for role in guild.me.roles]}')

@client.event
async def on_message(message):
    print(f"\n--- New Message ---")
    print(f"Author: {message.author} (Bot: {message.author.bot})")
    print(f"Channel: {message.channel.name} (ID: {message.channel.id})")
    print(f"Content: {message.content}")
    print(f"Guild: {message.guild}")
    print(f"Intents: {message.guild.me.guild_permissions if message.guild else 'No guild'}")

    # Ignore messages from the bot itself
    if message.author == client.user:
        print("Ignoring message from self")
        return
    
    # Check if message is in the correct channel
    print(f"Checking channel ID: {message.channel.id} (expected: {CHANNEL_ID})")
    if message.channel.id != CHANNEL_ID:
        print(f"Message not in target channel, ignoring")
        return
    
    # Check if message contains any Facebook video URLs
    urls = re.findall(r'https?://\S+', message.content)
    facebook_urls = [url for url in urls if is_facebook_video_url(url)]
    
    if not facebook_urls:
        return
    
    # Process each Facebook URL
    for url in facebook_urls:
        try:
            # Send initial processing message
            processing_msg = await message.channel.send(f"🔄 Processing {url}...")
            
            # Download the video
            output_dir = DOWNLOAD_DIR
            os.makedirs(output_dir, exist_ok=True)
            
            # Use the existing download function
            download_reel_as_mp4(url, output_dir)
            
            # Find the downloaded file (yt-dlp handles the filename)
            # We'll use the get_video_path function to get the expected path
            video_path = get_video_path(url)

            print(f"Video path: {video_path}")
            
            if os.path.exists(video_path):
                # Get the original message content without the URL
                original_text = message.content.replace(url, "").strip()
                
                # Get current timestamp
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Create a rich embed message
                embed = discord.Embed(
                    title="🎥 Video Shared",
                    description=original_text or "Check out this video!",
                    color=0x1DA1F2  # Twitter blue color
                )
                
                # Add fields with relevant information
                embed.add_field(name="👤 Shared by", value=f"{message.author.mention}", inline=True)
                embed.add_field(name="📅 Shared at", value=f"`{timestamp}`", inline=True)
                embed.add_field(name="🔗 Original URL", value=f"[View on Facebook]({url})", inline=False)
                
                # Set footer with additional info
                embed.set_footer(text="Facebook Video Bot", icon_url=message.guild.icon.url if message.guild and message.guild.icon else None)
                
                # Send the video with the embed
                with open(video_path, 'rb') as f:
                    video_file = discord.File(f, filename=os.path.basename(video_path))
                    await message.channel.send(
                        content=f"📢 @here New video shared!" if original_text else "📢 @here New video shared!",
                        file=video_file,
                        embed=embed
                    )
                
                # Clean up the video file
                try:
                    os.remove(video_path)
                except Exception as e:
                    print(f"Could not delete video file: {e}")
                
                # Delete the processing message
                await processing_msg.delete()

                # Delete the original message
                try:
                    await message.delete()
                except Exception as e:
                    print(f"Could not delete message: {e}")
            else:
                await message.channel.send("❌ Could not download the video. The link might be invalid or the video might be private.")

        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            await message.channel.send(f"❌ An error occurred while processing the video: {str(e)}")

        # Clean up the video file
        try:
            os.remove(video_path)
            print(f"Successfully deleted video file: {video_path}")
        except Exception as e:
            print(f"Could not delete video file: {e}")

# Run the bot
if __name__ == "__main__":
    try:
        print("\n=== Starting bot execution ===")
        
        # Create downloads directory if it doesn't exist
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        print(f"Created/verified download directory: {os.path.abspath(DOWNLOAD_DIR)}")
        
        # Check if token is set
        token = os.getenv('DISCORD_TOKEN')
        if not token or token == 'your_discord_bot_token_here':
            raise ValueError("Please set your Discord bot token in the .env file")
        
        # Remove quotes if present in the token
        token = token.strip('"\'')
        print("Discord token found and processed")
        
        # Verify channel ID
        print(f"Target channel ID: {CHANNEL_ID} (Type: {type(CHANNEL_ID)})")
        
        print("Attempting to start Discord client...")
        client.run(token, log_level=logging.DEBUG)
        
    except discord.LoginFailure:
        print("ERROR: Failed to login. Please check your bot token.")
    except discord.PrivilegedIntentsRequired:
        print("ERROR: Missing required intents. Please enable all required intents in the Discord Developer Portal.")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nBot has stopped.")
        if 'client' in locals() and not client.is_closed():
            print("Closing client...")
            client.loop.run_until_complete(client.close())
