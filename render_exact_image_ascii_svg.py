#!/usr/bin/env python3
"""Render exact pixel-accurate ASCII art from user's image into an animated SVG with cyan styling and line-by-line cascade."""

from PIL import Image
import numpy as np

def generate_exact_svg(img_path, output_path):
    img = Image.open(img_path).convert("RGBA")
    arr = np.array(img)
    
    # Text is dark pixels (r < 150, g < 150, b < 150)
    # Background is white (r > 200, g > 200, b > 200)
    gray = np.mean(arr[:, :, :3], axis=2)
    is_text = gray < 200
    
    # Find overall bounding box of text
    row_counts = is_text.sum(axis=1)
    col_counts = is_text.sum(axis=0)
    
    valid_rows = np.where(row_counts > 0)[0]
    valid_cols = np.where(col_counts > 0)[0]
    
    if len(valid_rows) == 0 or len(valid_cols) == 0:
        print("Error: No text found")
        return
        
    top_y = valid_rows[0]
    bottom_y = valid_rows[-1]
    left_x = valid_cols[0]
    right_x = valid_cols[-1]
    
    # Detect line regions
    lines = []
    in_line = False
    start_y = 0
    
    for y in range(top_y, bottom_y + 1):
        count = is_text[y, :].sum()
        if count > 1 and not in_line:
            in_line = True
            start_y = y
        elif count <= 1 and in_line:
            in_line = False
            lines.append((start_y, y - 1))
    if in_line:
        lines.append((start_y, bottom_y))
        
    print(f"Text box: x={left_x}..{right_x} (w={right_x-left_x+1}), y={top_y}..{bottom_y} (h={bottom_y-top_y+1})")
    print(f"Total lines detected: {len(lines)}")
    
    # Dimensions for SVG
    padding_x = 24
    padding_top = 40
    padding_bottom = 24
    
    scale = 0.75  # scale down slightly for perfect fit on GitHub profile (width ~ 600px)
    
    content_w = int((right_x - left_x + 1) * scale)
    content_h = int((bottom_y - top_y + 1) * scale)
    
    svg_w = padding_x * 2 + content_w
    svg_h = padding_top + padding_bottom + content_h
    
    svg = []
    svg.append(f'<svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}" fill="none" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">')
    svg.append('  <defs>')
    svg.append(f'    <linearGradient id="photoBorder" x1="0" y1="0" x2="{svg_w}" y2="{svg_h}" gradientUnits="userSpaceOnUse">')
    svg.append('      <stop offset="0%" stop-color="#22D3EE" stop-opacity="0.3"/>')
    svg.append('      <stop offset="50%" stop-color="#A855F7" stop-opacity="0.2"/>')
    svg.append('      <stop offset="100%" stop-color="#22D3EE" stop-opacity="0.3"/>')
    svg.append('    </linearGradient>')
    svg.append('  </defs>')
    svg.append('')
    # Dark container
    svg.append(f'  <rect width="{svg_w}" height="{svg_h}" rx="14" fill="#0A0A0F"/>')
    svg.append(f'  <rect x="0.5" y="0.5" width="{svg_w-1}" height="{svg_h-1}" rx="13.5" stroke="url(#photoBorder)" stroke-width="1"/>')
    
    # Title bar / traffic lights
    svg.append('  <circle cx="20" cy="18" r="4" fill="#FF5F57" opacity="0.8"/>')
    svg.append('  <circle cx="34" cy="18" r="4" fill="#FFBD2E" opacity="0.8"/>')
    svg.append('  <circle cx="48" cy="18" r="4" fill="#28CA42" opacity="0.8"/>')
    svg.append('  <text x="64" y="22" fill="#52525B" font-family="\'SF Mono\', \'Fira Code\', monospace" font-size="10">nova-os — exact_ascii_art.vector</text>')
    
    total_lines = len(lines)
    anim_duration = 2.5
    step_delay = anim_duration / max(total_lines, 1)
    
    # For each line, crop the line image, recolor dark text to cyan (#22D3EE), make background transparent, convert to PNG data URI
    import io, base64
    
    for idx, (sy, ey) in enumerate(lines):
        line_crop = arr[sy:ey+1, left_x:right_x+1].copy()
        
        # Create RGBA image for line: cyan (#22D3EE) where text was dark, transparent elsewhere
        line_h, line_w, _ = line_crop.shape
        rgba = np.zeros((line_h, line_w, 4), dtype=np.uint8)
        
        # Calculate darkness intensity (0 = black text = full cyan opacity, 255 = white bg = transparent)
        line_gray = np.mean(line_crop[:, :, :3], axis=2)
        alpha = np.clip((240.0 - line_gray) * 1.2, 0, 255).astype(np.uint8)
        
        # Set RGB to cyan (#22D3EE => R:34, G:211, B:238)
        rgba[:, :, 0] = 34
        rgba[:, :, 1] = 211
        rgba[:, :, 2] = 238
        rgba[:, :, 3] = alpha
        
        line_img = Image.fromarray(rgba, mode="RGBA")
        
        # Encode to PNG base64
        buf = io.BytesIO()
        line_img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        data_url = f"data:image/png;base64,{b64}"
        
        y_pos = int(padding_top + (sy - top_y) * scale)
        rendered_h = int(line_h * scale)
        rendered_w = int(line_w * scale)
        
        delay = 0.1 + idx * step_delay
        
        svg.append(f'  <g opacity="0">')
        svg.append(f'    <image x="{padding_x}" y="{y_pos}" width="{rendered_w}" height="{rendered_h}" xlink:href="{data_url}"/>')
        svg.append(f'    <animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.08s" fill="freeze"/>')
        svg.append(f'  </g>')
        
    svg.append('</svg>')
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
        
    print(f"Generated 100% exact vector ASCII SVG at {output_path} ({svg_w}x{svg_h}, {total_lines} lines)")

if __name__ == "__main__":
    generate_exact_svg(
        "/Users/smartcomputer/.gemini/antigravity-ide/brain/39fdf049-0485-4e67-aa25-8c8a814c9146/media__1786235028074.png",
        "/Users/smartcomputer/Git profile/Zcodeod-OG/assets/ascii_name.svg"
    )
