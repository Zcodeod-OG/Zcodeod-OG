#!/usr/bin/env python3
import xml.sax.saxutils as saxutils

def build_svg_from_txt(txt_path, output_path):
    with open(txt_path, 'r', encoding='utf-8') as f:
        raw_lines = f.read().splitlines()
        
    # Strip leading/trailing blank lines
    while raw_lines and not raw_lines[0].strip():
        raw_lines.pop(0)
    while raw_lines and not raw_lines[-1].strip():
        raw_lines.pop()
        
    if not raw_lines:
        print("Error: ascii-art.txt is empty")
        return

    # Find longest line width
    max_cols = max(len(l) for l in raw_lines)
    total_rows = len(raw_lines)

    padding_x = 20
    padding_top = 40
    padding_bottom = 20
    line_height = 11.5
    font_size = 9.5
    char_w = 5.8  # width of monospace char at 9.5px font

    svg_width = int(padding_x * 2 + max_cols * char_w)
    svg_height = int(padding_top + padding_bottom + total_rows * line_height)

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
    svg.append('  <text x="64" y="22" fill="#52525B" font-family="\'SF Mono\', \'Fira Code\', monospace" font-size="10">nova-os — ascii_art.txt</text>')

    # Cascade animation
    anim_duration = 2.2
    step_delay = anim_duration / max(total_rows, 1)

    for idx, line in enumerate(raw_lines):
        y_pos = padding_top + idx * line_height
        delay = 0.08 + idx * step_delay
        escaped = saxutils.escape(line)
        
        svg.append(
            f'  <text x="{padding_x}" y="{y_pos:.1f}" fill="#22D3EE" font-family="\'SF Mono\', \'Fira Code\', monospace" font-size="{font_size}" opacity="0" xml:space="preserve">{escaped}'
            f'<animate attributeName="opacity" from="0" to="0.92" begin="{delay:.2f}s" dur="0.06s" fill="freeze"/></text>'
        )

    svg.append('</svg>')

    with open(output_path, 'w', encoding='utf-8') as out:
        out.write('\n'.join(svg))

    print(f"Generated clean SVG from ascii-art.txt at {output_path} ({svg_width}x{svg_height}, {total_rows} lines)")

if __name__ == "__main__":
    build_svg_from_txt("ascii-art.txt", "assets/ascii_name.svg")
