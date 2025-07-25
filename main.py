import os
import sys
import subprocess
import re
import platform
import stat
import shutil
from pathlib import Path
import os
import sys

# Add the parent directory to the path so we can import utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import get_video_path

def setup_ffmpeg():
    """Set up FFmpeg locally if not already set up."""
    bin_dir = Path(__file__).parent / 'bin'
    ffmpeg_path = bin_dir / 'ffmpeg'
    
    # Create bin directory if it doesn't exist
    bin_dir.mkdir(exist_ok=True)
    
    if not ffmpeg_path.exists():
        print("FFmpeg not found. Setting up local FFmpeg...")
        
        if platform.system() == 'Darwin':  # macOS
            try:
                # Download FFmpeg static build from a reliable source
                import urllib.request
                import ssl
                import stat
                
                print("Downloading FFmpeg static build for macOS...")
                # Using a direct download link from BtbN's FFmpeg builds (macOS 64-bit)
                ffmpeg_url = "https://evermeet.cx/ffmpeg/ffmpeg-6.1.1.7z"
                
                # Create unverified SSL context
                ssl_context = ssl._create_unverified_context()
                
                # Download the binary with the unverified SSL context
                req = urllib.request.Request(ffmpeg_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, context=ssl_context) as response, \
                     open(ffmpeg_path, 'wb') as out_file:
                    # Directly save the binary (no gzip decompression needed)
                    shutil.copyfileobj(response, out_file)
                
                # Make FFmpeg executable
                ffmpeg_path.chmod(0o755)  # rwxr-xr-x
                print("FFmpeg has been installed successfully!")
                
            except Exception as e:
                print(f"Error setting up FFmpeg: {e}")
                print("Please install FFmpeg manually and ensure it's in your PATH.")
                sys.exit(1)
        else:
            print("Automatic FFmpeg setup is only available for macOS.")
            print("Please install FFmpeg manually and ensure it's in your PATH.")
            sys.exit(1)
    
    return str(ffmpeg_path.absolute())

def is_valid_facebook_reels_url(url):
    """Check if the provided URL is a valid Facebook Reels URL."""
    facebook_regex = r'https?://(?:www\.)?(facebook\.com|fb\.watch)/reel/.*'
    return re.match(facebook_regex, url) is not None

def is_valid_instagram_reels_url(url):
    """Check if the provided URL is a valid Instagram Reels URL."""
    instagram_regex = r'https?://(?:www\.)?instagram\.com/reel/.*'
    return re.match(instagram_regex, url) is not None

def is_valid_reels_url(url):
    """Check if the provided URL is a valid Facebook or Instagram Reels URL."""
    return is_valid_facebook_reels_url(url) or is_valid_instagram_reels_url(url)

def download_reel_as_mp4(url, output_dir='downloads', cookies_file='cookies.txt'):
    try:
        ffmpeg_path = setup_ffmpeg()
        os.makedirs(output_dir, exist_ok=True)
        import yt_dlp
        output_path = get_video_path(url)
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': output_path.replace('.mp4', '.%(ext)s'),
            'merge_output_format': 'mp4',
            'nocheckcertificate': True,
            'ffmpeg_location': os.path.dirname(ffmpeg_path),
            'quiet': False,
            'no_warnings': False
        }
        # Add cookies if file exists
        if os.path.exists(cookies_file):
            ydl_opts['cookiefile'] = cookies_file

        print(f"Downloading {url}...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Download completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading video: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python facebook_reels_downloader.py <reel_url>")
        sys.exit(1)
    
    url = sys.argv[1].strip()
    
    if not is_valid_reels_url(url):
        print("Error: Please provide a valid Facebook or Instagram Reels URL")
        print("Example Facebook: https://www.facebook.com/reel/1234567890/")
        print("Example Instagram: https://www.instagram.com/reel/XXXXXXXXXXX/")
        sys.exit(1)
    
    download_reel_as_mp4(url)

if __name__ == "__main__":
    main()
