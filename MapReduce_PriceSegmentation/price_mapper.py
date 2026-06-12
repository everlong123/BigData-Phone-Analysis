import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    
    parts = line.split(',')
    
    # Check if the row has enough columns (at least 8 columns to reach index 7)
    if len(parts) < 8:
        continue
        
    try:
        # EXACT COLUMN: Column H in Excel corresponds to parts[7]
        price_str = parts[7].strip()
        
        # Clean string to keep only numeric characters
        cleaned_price = ''.join(c for c in price_str if c.isdigit())
        
        if not cleaned_price:
            continue
            
        price = float(cleaned_price)
        
        # Segmentation logic based on your rules
        if price < 35000000:
            segment = "Budget"
        elif price <= 45000000:
            segment = "Mid-range"
        else:
            segment = "Premium"
            
        print(f"{segment}\t1")
        
    except (ValueError, IndexError):
        continue