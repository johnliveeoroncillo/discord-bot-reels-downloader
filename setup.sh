#!/bin/bash

# Create bin directory if it doesn't exist
mkdir -p bin

# Download FFmpeg for macOS
if [[ "$(uname)" == "Darwin" ]]; then
    echo "Downloading FFmpeg for macOS..."
    curl -L https://evermeet.cx/ffmpeg/ffmpeg-6.1.1.7z -o ffmpeg.7z
    
    # Install 7z if not installed
    if ! command -v 7z &> /dev/null; then
        echo "Installing p7zip..."
        brew install p7zip
    fi
    
    # Extract FFmpeg
    7z x ffmpeg.7z -obin/
    chmod +x bin/ffmpeg
    rm ffmpeg.7z
    
    echo "FFmpeg has been installed to bin/ffmpeg"
else
    echo "This setup script is for macOS only. Please install FFmpeg manually for your system."
    exit 1
fi

echo "Setup complete!"
