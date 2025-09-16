#!/bin/bash

# Try different audio drivers in order of preference
export SDL_AUDIODRIVER=pulse  # Try PulseAudio first
python main.py

if [ $? -ne 0 ]; then
    echo "Failed with pulse driver, trying ALSA..."
    export SDL_AUDIODRIVER=alsa  # Try ALSA second
    python main.py
fi

if [ $? -ne 0 ]; then
    echo "Failed with ALSA driver, trying dummy..."
    export SDL_AUDIODRIVER=dummy  # Use dummy as fallback
    python main.py
fi