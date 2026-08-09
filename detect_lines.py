#!/usr/bin/env python3
from PIL import Image
import numpy as np

img = Image.open('/Users/smartcomputer/.gemini/antigravity-ide/brain/39fdf049-0485-4e67-aa25-8c8a814c9146/media__1786235028074.png').convert('L')
arr = np.array(img)

# Binary mask: True where text is present (dark pixels < 128)
mask = arr < 128

# Sum across columns to find line rows
row_counts = mask.sum(axis=1)

lines = []
in_line = False
start_y = 0

for y, count in enumerate(row_counts):
    if count > 2 and not in_line:
        in_line = True
        start_y = y
    elif count <= 2 and in_line:
        in_line = False
        end_y = y
        lines.append((start_y, end_y))

print(f"Detected {len(lines)} line regions:")
for idx, (sy, ey) in enumerate(lines):
    print(f"Line {idx+1:02d}: y={sy}..{ey} (height={ey-sy})")
