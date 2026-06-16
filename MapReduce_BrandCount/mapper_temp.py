#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
        
    # Find the first comma (end of Product_ID)
    first_comma = line.find(',')
    if first_comma == -1:
        continue
        
    # Find the second comma (end of Product_Name)
    # This correctly skips any text inside Product_Name
    second_comma = line.find(',', first_comma + 1)
    if second_comma == -1:
        continue
        
    # Find the third comma (end of Brand)
    third_comma = line.find(',', second_comma + 1)
    if third_comma == -1:
        # If there is no third comma, the rest of the line is the Brand
        brand = line[second_comma + 1:].strip()
    else:
        brand = line[second_comma + 1:third_comma].strip()
        
    if brand:
        # Standard Output with clear tab separation
        sys.stdout.write(f"{brand}\t1\n")