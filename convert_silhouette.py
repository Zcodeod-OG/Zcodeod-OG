#!/usr/bin/env python3
from PIL import Image, ImageEnhance, ImageOps
import sys

INPUT_PATH = sys.argv[1]
OUTPUT_PATH = sys.argv[2]

def convert_silhouette(img_path, output_path, ascii_width=85):
    img = Image.open(img_path).convert("L")
    
    # Invert image so dark characters become bright pixels
    inverted = ImageOps.invert(img)
    
    # Bounding box crop to trim top/bottom whitespace
    bbox = inverted.getbbox()
    if bbox:
        # Give a small padding
        w, h = inverted.size
        left = max(0, bbox[0] - 10)
        top = max(0, bbox[1] - 10)
        right = min(w, bbox[2] + 10)
        bottom = min(h, bbox[3] + 10)
        cropped = inverted.crop((left, top, right, bottom))
    else:
        cropped = inverted
        
    # Contrast enhancement for sharp ASCII edges
    cropped = ImageEnhance.Contrast(cropped).enhance(2.5)
    
    aspect = cropped.height / cropped.width
    ascii_height = int(ascii_width * aspect * 0.48)
    
    resized = cropped.resize((ascii_width, ascii_height), Image.Resampling.LANCZOS)
    pixels = list(resized.get_flattened_data())
    
    # Character set matching density (from space to dense blocks)
    CHAR_SET = ' .`^",:;Il!i>~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#%@█'
    
    lines = []
    for r in range(ascii_height):
        row_str = ""
        for c in range(ascii_width):
            val = pixels[r * ascii_width + c]
            idx = int(val / 256 * len(CHAR_SET))
            idx = min(idx, len(CHAR_SET) - 1)
            row_str += CHAR_SET[idx]
        lines.append(row_str)
        
    # Now generate SVG
    padding_x = 24
    padding_top = 40
    padding_bottom = 24
    line_height = 12
    font_size = 10.5
    char_w = 6.4
    
    svg_width = int(padding_x * 2 + ascii_width * char_w)
    svg_height = int(padding_top + padding_bottom + ascii_height * line_height)
    
    svg = []
    svg.append(f'<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" fill="none" xmlns="http://www.w3.org/2000/svg">')
    svg.append('  <defs>')
    svg.append(f'    <linearGradient id="photoBorder" x1="0" y1="0" x2="{svg_width}" y2="{svg_height}" gradientUnits="userSpaceOnUse">')
    svg.append('      <stop offset="0%" stop-color="#22D3EE" stop-opacity="0.3"/>')
    svg.append('      <stop offset="50%" stop-color="#A855F7" stop-opacity="0.2"/>')
    svg.append('      <stop offset="100%" stop-color="#22D3EE" stop-opacity="0.3"/>')
    svg.append('    </linearGradient>')
    svg.append('  </defs>')
    svg.append('')
    # Dark container
    svg.append(f'  <rect width="{svg_width}" height="{svg_height}" rx="14" fill="#0A0A0F"/>')
    svg.append(f'  <rect x="0.5" y="0.5" width="{svg_width-1}" height="{svg_height-1}" rx="13.5" stroke="url(#photoBorder)" stroke-width="1"/>')
    
    # Title bar / traffic lights
    svg.append('  <circle cx="20" cy="18" r="4" fill="#FF5F57" opacity="0.8"/>')
    svg.append('  <circle cx="34" cy="18" r="4" fill="#FFBD2E" opacity="0.8"/>')
    svg.append('  <circle cx="48" cy="18" r="4" fill="#28CA42" opacity="0.8"/>')
    svg.append('  <text x="64" y="22" fill="#52525B" font-family="\'SF Mono\', \'Fira Code\', monospace" font-size="10">nova-os — ascii_silhouette_matrix.art</text>')
    
    # Lines animation
    total_lines = len(lines)
    anim_duration = 2.4  # seconds cascade
    step_delay = anim_duration / max(total_lines, 1)
    
    for idx, line in enumerate(lines):
        y_pos = padding_top + idx * line_height
        delay = 0.1 + idx * step_delay
        
        escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        
        svg.append(
            f'  <text x="{padding_x}" y="{y_pos}" fill="#22D3EE" font-family="\'SF Mono\', \'Fira Code\', monospace" font-size="{font_size}" opacity="0" xml:space="preserve">{escaped}'
            f'<animate attributeName="opacity" from="0" to="0.9" begin="{delay:.2f}s" dur="0.08s" fill="freeze"/></text>'
        )
        
    svg.append('</svg>')
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
        
    print(f"Generated silhouette SVG at {output_path} ({svg_width}x{svg_height}, {total_lines} lines)")
    
    print("\n--- Preview first 15 lines ---")
    for l in lines[:15]:
        print(l)

if __name__ == "__main__":
    convert_silhouette(INPUT_PATH, OUTPUT_PATH, 85)
