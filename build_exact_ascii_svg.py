#!/usr/bin/env python3
"""Build exact ASCII SVG from extracted text lines."""

import sys
import xml.sax.saxutils as saxutils

def build_exact_ascii_svg(text_lines, output_path):
    # Remove trailing empty lines
    while text_lines and not text_lines[-1].strip():
        text_lines.pop()
    while text_lines and not text_lines[0].strip():
        text_lines.pop(0)
        
    max_len = max(len(line) for line in text_lines) if text_lines else 80
    
    padding_x = 24
    padding_top = 40
    padding_bottom = 24
    line_height = 12
    font_size = 10.5
    char_w = 6.4
    
    svg_width = int(padding_x * 2 + max_len * char_w)
    svg_height = int(padding_top + padding_bottom + len(text_lines) * line_height)
    
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
    svg.append('  <text x="64" y="22" fill="#52525B" font-family="\'SF Mono\', \'Fira Code\', monospace" font-size="10">nova-os — exact_ascii_art.matrix</text>')
    
    # Cascade animation
    total_lines = len(text_lines)
    anim_duration = 2.4
    step_delay = anim_duration / max(total_lines, 1)
    
    for idx, line in enumerate(text_lines):
        y_pos = padding_top + idx * line_height
        delay = 0.1 + idx * step_delay
        escaped = saxutils.escape(line)
        
        svg.append(
            f'  <text x="{padding_x}" y="{y_pos}" fill="#22D3EE" font-family="\'SF Mono\', \'Fira Code\', monospace" font-size="{font_size}" opacity="0" xml:space="preserve">{escaped}'
            f'<animate attributeName="opacity" from="0" to="0.95" begin="{delay:.2f}s" dur="0.08s" fill="freeze"/></text>'
        )
        
    svg.append('</svg>')
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
        
    print(f"Generated exact ASCII SVG at {output_path} ({svg_width}x{svg_height}, {total_lines} lines)")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        output = sys.argv[2] if len(sys.argv) > 2 else "assets/ascii_name.svg"
        build_exact_ascii_svg(lines, output)
