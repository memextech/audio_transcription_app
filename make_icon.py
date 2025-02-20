from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, emoji, output_path):
    # Create a new image with a transparent background
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Load a font that supports emoji (Apple Color Emoji for macOS)
    font_size = int(size * 0.8)  # Make emoji slightly smaller than the canvas
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Apple Color Emoji.ttc', font_size)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position to center the emoji
    left, top, right, bottom = font.getbbox(emoji)
    w = right - left
    h = bottom - top
    x = (size - w) / 2
    y = (size - h) / 2
    
    # Draw the emoji
    draw.text((x, y), emoji, font=font, embedded_color=True)
    
    # Save the image
    image.save(output_path)

# Create icons directory
if not os.path.exists('icons'):
    os.makedirs('icons')

# Create icons of different sizes
sizes = [16, 32, 64, 128, 256, 512, 1024]
for size in sizes:
    create_icon(size, "🎙️", f"icons/icon_{size}x{size}.png")

# Create icns file using iconutil
os.system("mkdir -p icons.iconset")
for size in sizes:
    os.system(f"cp icons/icon_{size}x{size}.png icons.iconset/icon_{size}x{size}.png")
    if size <= 512:  # Create @2x versions for retina displays
        os.system(f"cp icons/icon_{size*2}x{size*2}.png icons.iconset/icon_{size}x{size}@2x.png")

os.system("iconutil -c icns icons.iconset -o icons/AppIcon.icns")
os.system("rm -rf icons.iconset")  # Clean up
