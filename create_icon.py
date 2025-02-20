#!/usr/bin/env python3
import os
import sys
from PIL import Image, ImageDraw

def create_rounded_icon(input_path, output_path, corner_radius=40):
    # Open the image
    img = Image.open(input_path).convert('RGBA')
    
    # Resize to 1024x1024 (standard macOS app icon size)
    img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
    
    # Create mask for rounded corners
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), img.size], corner_radius, fill=255)
    
    # Apply mask
    output = Image.new('RGBA', img.size, (0, 0, 0, 0))
    output.paste(img, mask=mask)
    
    # Save the output
    output.save(output_path, 'PNG')

def create_icns(png_path, icns_dir):
    # Create temporary iconset directory
    iconset_path = os.path.join(icns_dir, 'AppIcon.iconset')
    os.makedirs(iconset_path, exist_ok=True)
    
    # Icon sizes required by macOS
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    # Generate each size
    for size in sizes:
        img = Image.open(png_path)
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        
        # Save regular size
        img.save(os.path.join(iconset_path, f'icon_{size}x{size}.png'))
        
        # Save @2x size (except for 1024)
        if size < 512:
            img = Image.open(png_path)
            img = img.resize((size*2, size*2), Image.Resampling.LANCZOS)
            img.save(os.path.join(iconset_path, f'icon_{size}x{size}@2x.png'))
    
    # Convert iconset to icns using iconutil
    os.system(f'iconutil -c icns {iconset_path}')
    
    # Clean up iconset directory
    os.system(f'rm -rf {iconset_path}')

if __name__ == '__main__':
    # Get project root directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths relative to project directory
    input_png = os.path.join(project_dir, 'assets', 'audio_transcriber_icon.png')
    rounded_png = os.path.join(project_dir, 'assets', 'audio_transcriber_icon_rounded.png')
    icons_dir = os.path.join(project_dir, 'assets')
    
    # Create rounded icon
    create_rounded_icon(input_png, rounded_png)
    
    # Create icns file
    create_icns(rounded_png, icons_dir)
    
    # Clean up rounded PNG
    os.remove(rounded_png)
    
    print(f"Icon generation complete. ICNS file available at: {os.path.join(icons_dir, 'AppIcon.icns')}")
