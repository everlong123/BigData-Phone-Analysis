import sys

current_key        = None
records            = []
total_input        = 0
total_clean        = 0
total_dupes        = 0
cross_source_dupes = 0
same_source_dupes  = 0


def parse_key(key):
    """Tách key thành 4 trường: norm_name, brand, ram, storage."""
    parts = key.split('|', 3)
    return parts if len(parts) == 4 else (key, '', '', '')


def pick_best(records):
    def sort_key(rec):
        source, name, price_str, pid = rec
        try:
            price = int(price_str)
        except ValueError:
            price = 999999999
        source_priority = 0 if source == "CellphoneS" else 1
        return (price, source_priority)
    return sorted(records, key=sort_key)[0]


def process_group(key, records):
    global total_input, total_clean, total_dupes
    global cross_source_dupes, same_source_dupes

    total_input += len(records)

    # Lấy brand/ram/storage từ key
    norm_name, brand, ram, storage = parse_key(key)

    if len(records) == 1:
        source, name, price, pid = records[0]
        print(f"CLEAN\t{pid}\t{name}\t{brand}\t{ram}\t{storage}\t{price}\t{source}")
        total_clean += 1
        return

    # Có trùng lặp
    total_dupes += len(records)
    sources_set = set(r[0] for r in records)

    if len(sources_set) > 1:
        cross_source_dupes += 1
        dup_type = "CROSS_SOURCE"
    else:
        same_source_dupes += 1
        dup_type = "SAME_SOURCE"

    print(f"\n{'='*70}")
    print(f"DUPLICATE [{dup_type}] - {len(records)} ban trung | Key: {key[:60]}")
    print(f"{'='*70}")

    for i, r in enumerate(records, 1):
        source, name, price_str, pid = r
        try:
            price_fmt = f"{int(price_str):,}"
        except ValueError:
            price_fmt = price_str
        print(f"  [{i}] {source:<14} | {pid:<20} | {price_fmt:>12} VND | {name[:45]}")

    best = pick_best(records)
    source, name, price_str, pid = best
    try:
        price_fmt = f"{int(price_str):,}"
    except ValueError:
        price_fmt = price_str

    print(f"  >>> GIU LAI: [{source}] {pid} - {price_fmt} VND")
    print(f"CLEAN\t{pid}\t{name}\t{brand}\t{ram}\t{storage}\t{price_str}\t{source}")
    total_clean += 1


for line in sys.stdin:
    line = line.rstrip('\n')
    if not line:
        continue

    try:
        key, value = line.split('\t', 1)
    except ValueError:
        continue

    parts = value.split('|', 3)
    if len(parts) < 4:
        continue

    if key != current_key:
        if current_key is not None:
            process_group(current_key, records)
        current_key = key
        records = [parts]
    else:
        records.append(parts)

# Xử lý nhóm cuối
if current_key is not None:
    process_group(current_key, records)

# Thống kê
removed = total_input - total_clean
print(f"\n{'#'*70}")
print(f"  THONG KE KET QUA MR4 - DATA DEDUPLICATION")
print(f"{'#'*70}")
print(f"  Tong ban ghi dau vao    : {total_input:>6}")
print(f"  Tong ban ghi duy nhat   : {total_clean:>6}  (giu lai)")
print(f"  Tong ban ghi xoa bo     : {removed:>6}  (trung lap)")
print(f"  Ti le trung lap         : {removed/total_input*100:.1f}%")
print(f"  ---")
print(f"  Nhom trung giua 2 nguon : {cross_source_dupes:>6}  (CellphoneS vs TGDD)")
print(f"  Nhom trung cung nguon   : {same_source_dupes:>6}  (cung source)")
print(f"{'#'*70}")
