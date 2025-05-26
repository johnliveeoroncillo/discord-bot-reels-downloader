import os
import re
import hashlib
from urllib.parse import urlparse

def get_video_path(url, download_dir='downloads'):
    """
    Generate a safe and unique filename for the downloaded video.
    Handles various Facebook URL formats and ensures the filename is valid.
    """
    # Clean the URL by removing tracking parameters and fragments
    clean_url = re.sub(r'[?&]fbclid=.*$', '', url.split('#')[0])
    
    # Try to extract video ID from different URL patterns
    video_id = None
    
    # Pattern 1: /reel/ID
    reel_match = re.search(r'/reel/([^/?&#]+)', clean_url)
    if reel_match:
        video_id = reel_match.group(1)
    
    # Pattern 2: /watch/?v=ID
    if not video_id:
        watch_match = re.search(r'/watch/\?v=([^&]+)', clean_url)
        if watch_match:
            video_id = watch_match.group(1)
    
    # Pattern 3: /share/r/ID
    if not video_id:
        share_match = re.search(r'/share/r/([^/]+)', clean_url)
        if share_match:
            video_id = share_match.group(1)
    
    # If no specific pattern matched, create a hash of the URL
    if not video_id:
        url_hash = hashlib.md5(clean_url.encode('utf-8')).hexdigest()[:8]
        video_id = f"fb_{url_hash}"
    
    # Clean the video ID to ensure it's filesystem-safe
    safe_id = re.sub(r'[^a-zA-Z0-9_-]', '_', str(video_id))
    
    # Ensure the download directory exists
    os.makedirs(download_dir, exist_ok=True)
    
    # Return full path with .mp4 extension
    return os.path.join(download_dir, f"{safe_id}.mp4")
