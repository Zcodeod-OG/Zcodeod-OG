#!/usr/bin/env python3
"""Convert user photo to detailed ASCII art and output as an animated SVG with line-by-line cascade."""

from PIL import Image, ImageEnhance, ImageOps
import sys

INPUT_PATH = sys.argv[1]
OUTPUT_PATH = sys.argv[2]

# ASCII config
ASCII_WIDTH = 90  # Detailed character width
LINE_HEIGHT = 12
FONT_SIZE = 10.5

# High detail character scale (from darkest to brightest for dark background)
CHAR_SET = ' .`^\",:;Il!i>~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#%@█'

def generate_ascii(img_path, width=90):
    img = Image.open(img_path)
    
    # Auto rotate if EXIF orientation exists
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass
        
    img = img.convert("L")
    
    # Enhance contrast and sharpness for clear facial features
    img = ImageEnhance.Contrast(img).enhance(2.2)
    img = ImageEnhance.Brightness(img).enhance(1.25)
    img = ImageEnhance.Sharpness(img).enhance(2.0)
    
    # Calculate aspect ratio
    aspect = img.height / img.width
    height = int(width * aspect * 0.48)
    
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    
    # Convert pixels to ASCII
    pixels = list(img.get_flattened_data())
    
    lines = []
    for r in range(height):
        row_str = ""
        for c in range(width):
            val = pixels[r * width + c]
            idx = int(val / 256 * len(CHAR_SET))
            idx = min(idx, len(CHAR_SET) - 1)
            row_str += CHAR_SET[idx]
        lines.append(row_str)
    return lines, width, height

def create_animated_svg(lines, width_chars, height_chars, output_path):
    padding_x = 24
    padding_top = 40
    padding_bottom = 24
    
    char_w = 6.4  # precise monospace char width at 10.5px Fira Code
    svg_width = int(padding_x * 2 + width_chars * char_w)
    svg_height = int(padding_top + padding_bottom + height_chars * LINE_HEIGHT)
    
    svg = []
    svg.append(f'<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" fill="none" xmlns="http://www.w3.org/2000/svg">')
    svg.append('  <defs>')
    svg.append(f'    <linearGradient id="photoBorder" x1="0" y1="0" x2="{svg_width}" y2="{svg_height}" gradientUnits="userSpaceOnUse">')
    svg.append('      <stop offset="0%" stop-color="#22D3EE" stop-opacity="0.3"/>')
    svg.append('      <stop offset="50%" stop-color="#A855F7" stop-opacity="0.2"/>')
    svg.append('      <stop offset="100%" stop-color="#22D3EE" stop-opacity="0.3"/>')
    svg.append('    </linearGradient>')
    svg.append('    <filter id="cyanGlow">')
    svg.append('      <feGaussianBlur stdDeviation="1.5" result="blur"/>')
    svg.append('      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>')
    svg.append('    </filter>')
    svg.append('  </defs>')
    svg.append('')
    # Dark container
    svg.append(f'  <rect width="{svg_width}" height="{svg_height}" rx="14" fill="#0A0A0F"/>')
    svg.append(f'  <rect x="0.5" y="0.5" width="{svg_width-1}" height="{svg_height-1}" rx="13.5" stroke="url(#photoBorder)" stroke-width="1"/>')
    
    # Title bar / traffic lights
    svg.append('  <circle cx="20" cy="18" r="4" fill="#FF5F57" opacity="0.8"/>')
    svg.append('  <circle cx="34" cy="18" r="4" fill="#FFBD2E" opacity="0.8"/>')
    svg.append('  <circle cx="48" cy="18" r="4" fill="#28CA42" opacity="0.8"/>')
    svg.append('  <text x="64" y="22" fill="#52525B" font-family="\'SF Mono\', \'Fira Code\', monospace" font-size="10">nova-os — visual_neural_render.ascii</text>')
    
    # Lines animation
    total_lines = len(lines)
    anim_duration = 2.4  # seconds cascade
    step_delay = anim_duration / total_lines
    
    for idx, line in enumerate(lines):
        y_pos = padding_top + idx * LINE_HEIGHT
        delay = 0.1 + idx * step_delay
        
        escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        
        svg.append(
            f'  <text x="{padding_x}" y="{y_pos}" fill="#22D3EE" font-family="\'SF Mono\', \'Fira Code\', monospace" font-size="{FONT_SIZE}" opacity="0" xml:space="preserve">{escaped}'
            f'<animate attributeName="opacity" from="0" to="0.9" begin="{delay:.2f}s" dur="0.08s" fill="freeze"/></text>'
        )
        
    svg.append('</svg>')
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated animated ASCII SVG at {output_path} ({svg_width}x{svg_height}, {total_lines} lines)")

if __name__ == "__main__":
    lines, w, h = generate_ascii(INPUT_PATH, ASCII_WIDTH)
    create_animated_svg(lines, w, h, OUTPUT_PATH)
