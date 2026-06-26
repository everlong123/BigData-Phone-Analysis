#!/usr/bin/env python3
import sys
import csv
import re

HEADER_KEYWORDS = {"product_id", "product_name", "ten", "name", "id"}

def is_header(row):
    return row[0].strip().lower() in HEADER_KEYWORDS

def normalize_name(name):
    name = name.lower().strip()
    for prefix in ["dien thoai ", "smartphone ", "điện thoại "]:
        if name.startswith(prefix):
            name = name[len(prefix):]
    name = re.sub(r'\s*-\s*(moi|hang trung bay|new|refurbished|cu|like new).*$', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    try:
        row = next(csv.reader([line]))
    except Exception:
        continue

    if len(row) < 12:
        continue

    if is_header(row):
        continue

    try:
        product_id   = row[0].strip()
        product_name = row[1].strip()
        brand        = row[2].strip().lower()
        ram          = row[4].strip().lower()
        storage      = row[5].strip().lower()
        sale_price   = row[7].strip()
        source       = row[10].strip()

        if not product_name:
            continue

        norm_name   = normalize_name(product_name)
        product_key = f"{norm_name}|{brand}|{ram}|{storage}"

        value = f"{source}|{product_name}|{sale_price}|{product_id}"

        print(f"{product_key}\t{value}")

    except (ValueError, IndexError):
        continue
