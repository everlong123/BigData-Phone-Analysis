#!/usr/bin/env python3
import sys

current_brand = None
current_count = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
        
    # Standard split by tab character
    if '\t' not in line:
        continue
        
    brand, count = line.split('\t', 1)
    
    try:
        count = int(count)
    except ValueError:
        continue

    if current_brand == brand:
        current_count += count
    else:
        if current_brand:
            sys.stdout.write(f"{current_brand}\t{current_count}\n")
        current_brand = brand
        current_count = count

if current_brand:
    sys.stdout.write(f"{current_brand}\t{current_count}\n")