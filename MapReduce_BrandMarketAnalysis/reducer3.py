import sys

current_brand = None
prices        = [] 
results       = []


def process_brand(brand, prices):
    count   = len(prices)
    avg     = sum(prices) // count
    min_p   = min(prices)
    max_p   = max(prices)
    results.append((count, brand, avg, min_p, max_p))


for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    try:
        brand, price_str = line.split("\t", 1)
        sale_price = int(price_str)
    except (ValueError, IndexError):
        continue

    if brand != current_brand:
        if current_brand is not None:
            process_brand(current_brand, prices)
        current_brand = brand
        prices = [sale_price]
    else:
        prices.append(sale_price)

# Xử lý hãng cuối cùng
if current_brand is not None:
    process_brand(current_brand, prices)

# Sắp xếp theo số lượng sản phẩm giảm dần
results.sort(reverse=True)

# In bảng kết quả
print("=" * 72)
print(f"{'HANG':<16} {'SO LUONG':>9} {'GIA TB (VND)':>14} {'GIA THAP NHAT':>14} {'GIA CAO NHAT':>14}")
print("=" * 72)

for count, brand, avg, min_p, max_p in results:
    print(f"{brand:<16} {count:>9} {avg:>14,} {min_p:>14,} {max_p:>14,}")

print("=" * 72)
print(f"  Tong so hang: {len(results)}")
print(f"  Tong san pham: {sum(r[0] for r in results)}")
print("=" * 72)
