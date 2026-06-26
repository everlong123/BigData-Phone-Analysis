import sys
import csv

HEADER_KEYWORDS = {"product_id", "product_name", "ten", "name"}

def is_header(row):
    return row[0].strip().lower() in HEADER_KEYWORDS

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    try:
        row = next(csv.reader([line]))
    except Exception:
        continue

    if len(row) < 8:
        continue

    if is_header(row):
        continue

    try:
        brand      = row[2].strip().lower()
        sale_price = int(row[7].strip())

        if not brand or sale_price <= 0:
            continue

        print(f"{brand}\t{sale_price}")

    except (ValueError, IndexError):
        continue
