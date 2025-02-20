#!/bin/bash

# Create icons directory
mkdir -p icons.iconset

# Generate different icon sizes from the original
sips -z 16 16     ~/Downloads/audio_transcriber_icon.png --out icons.iconset/icon_16x16.png
sips -z 32 32     ~/Downloads/audio_transcriber_icon.png --out icons.iconset/icon_16x16@2x.png
sips -z 32 32     ~/Downloads/audio_transcriber_icon.png --out icons.iconset/icon_32x32.png
sips -z 64 64     ~/Downloads/audio_transcriber_icon.png --out icons.iconset/icon_32x32@2x.png
sips -z 128 128   ~/Downloads/audio_transcriber_icon.png --out icons.iconset/icon_128x128.png
sips -z 256 256   ~/Downloads/audio_transcriber_icon.png --out icons.iconset/icon_128x128@2x.png
sips -z 256 256   ~/Downloads/audio_transcriber_icon.png --out icons.iconset/icon_256x256.png
sips -z 512 512   ~/Downloads/audio_transcriber_icon.png --out icons.iconset/icon_256x256@2x.png
sips -z 512 512   ~/Downloads/audio_transcriber_icon.png --out icons.iconset/icon_512x512.png
sips -z 1024 1024 ~/Downloads/audio_transcriber_icon.png --out icons.iconset/icon_512x512@2x.png

# Convert to icns
iconutil -c icns icons.iconset -o icons/AppIcon.icns

# Clean up
rm -rf icons.iconset
