#!/usr/bin/env python3
import sys

# Use a dictionary to store counts for each segment
segment_counts = {}

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
        
    if '\t' not in line:
        continue
        
    try:
        segment, count_str = line.split('\t', 1)
        count = int(count_str.strip())
        
        # Accumulate the count for each segment safely
        segment_counts[segment] = segment_counts.get(segment, 0) + count
    except ValueError:
        continue

# Print all accumulated results
for segment, total_count in segment_counts.items():
    print(f"{segment}\t{total_count}")