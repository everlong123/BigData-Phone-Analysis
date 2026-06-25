import sys
import requests
import json
import csv
import time
import random
import re
from datetime import datetime

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUTPUT_FILE     = "products_cellphones.csv"
GRAPHQL_URL     = "https://api.cellphones.com.vn/v2/graphql/query"
CATEGORY_ID     = "3"
PAGE_SIZE       = 50
DELAY_MIN       = 1.0
DELAY_MAX       = 2.5
REQUEST_TIMEOUT = 20

PROVINCES = [1, 2, 3, 48, 77, 31, 45, 92, 58, 74]

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Origin": "https://cellphones.com.vn",
    "Referer": "https://cellphones.com.vn/mobile.html",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
}

FIELDS = [
    "product_id", "product_name", "brand", "model_series",
    "ram_capacity", "rom_capacity", "original_price", "sale_price",
    "stock_status", "product_status", "source_site", "crawl_date"
]

def build_query(page: int, size: int, province_id: int = 1) -> str:
    return f"""query GetProductsByCateId{{
    products(
        filter: {{
            static: {{
                province_id: {province_id},
                categories: ["{CATEGORY_ID}"]
            }},
            dynamic: {{}}
        }},
        page: {page},
        size: {size}
    )
    {{
        general{{
            product_id
            name
            attributes
            sku
            manufacturer
            url_key
        }},
        filterable{{
            stock
            price
            prices
            special_price
            display_root_price
            display_price
        }},
    }}
}}"""

def parse_ram_rom_from_name(name: str) -> tuple[str, str]:
    matches = re.findall(r'(\d+(?:\.\d+)?)\s*(GB|TB)', name, re.IGNORECASE)
    ram, rom = "N/A", "N/A"
    if len(matches) >= 2:

        sizes = []
        for m in matches:
            val_gb = float(m[0]) * (1024 if m[1].upper() == 'TB' else 1)
            sizes.append((val_gb, m[0], m[1].upper()))
        sizes.sort(key=lambda x: x[0])
        ram = f"{int(float(sizes[0][1]))}{sizes[0][2]}"
        rom = f"{int(float(sizes[-1][1]))}{sizes[-1][2]}"
    elif len(matches) == 1:
        rom = f"{int(float(matches[0][0]))}{matches[0][1].upper()}"
    return ram, rom

def parse_ram_rom_from_attributes(attributes) -> tuple[str, str]:
    ram, rom = "N/A", "N/A"
    if not attributes:
        return ram, rom
    if isinstance(attributes, list):
        for attr in attributes:
            if not isinstance(attr, dict): continue
            name_lower = str(attr.get("name", "")).lower()
            value = str(attr.get("value", "")).strip()
            if any(k in name_lower for k in ["ram", "memory_internal", "mobile_ram"]):
                ram = value
            elif any(k in name_lower for k in ["rom", "bộ nhớ trong", "storage", "mobile_storage"]):
                rom = value
    elif isinstance(attributes, dict):
        ram = (attributes.get("mobile_ram_filter") or attributes.get("memory_internal") or "N/A")
        rom = (attributes.get("mobile_storage_filter") or attributes.get("storage") or "N/A")
    return ram or "N/A", rom or "N/A"

def extract_model_series(name: str) -> str:
    model = re.sub(r'\s*\|.*$', '', name).strip()
    model = re.sub(r'\b\d+(?:\.\d+)?\s*(?:GB|TB)\b', '', model, flags=re.IGNORECASE).strip()
    model = re.sub(r'\b(?:5G|4G|3G|NFC)\b', '', model, flags=re.IGNORECASE).strip()
    model = re.sub(r'\s*\([^)]*\)', '', model).strip()
    model = re.sub(r'\s+', ' ', model).strip()
    return model or "N/A"

def safe_price(val) -> int:
    if val is None: return 0
    try:
        v = int(float(str(val).replace(",", "")))
        return v if 0 < v < 500_000_000 else 0
    except:
        return 0

def process_product(prod: dict) -> dict | None:
    gen  = prod.get("general")  or {}
    filt = prod.get("filterable") or {}
    if not gen: return None

    name  = (gen.get("name") or "").strip()
    brand = (gen.get("manufacturer") or "").strip() or "N/A"

    attributes = gen.get("attributes")
    ram, rom = parse_ram_rom_from_attributes(attributes)
    if ram == "N/A" or rom == "N/A":
        p_ram, p_rom = parse_ram_rom_from_name(name)
        if ram == "N/A": ram = p_ram
        if rom == "N/A": rom = p_rom

    sale_price     = safe_price(filt.get("display_price") or filt.get("price") or filt.get("special_price"))
    original_price = safe_price(filt.get("display_root_price") or filt.get("prices"))
    if original_price == 0: original_price = sale_price
    if original_price < sale_price: original_price = sale_price

    stock_qty    = int(filt.get("stock") or 0)
    stock_status = "In Stock" if stock_qty > 0 else "Out of Stock"

    return {
        "product_id":     gen.get("product_id", gen.get("sku", "N/A")),
        "product_name":   name,
        "brand":          brand,
        "model_series":   extract_model_series(name),
        "ram_capacity":   ram,
        "rom_capacity":   rom,
        "original_price": original_price,
        "sale_price":     sale_price,
        "stock_status":   stock_status,
        "product_status": "Active",
        "source_site":    "cellphones.com.vn",
        "crawl_date":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

def fetch_page(page: int, size: int, province_id: int = 1) -> tuple[list, bool]:
    query   = build_query(page, size, province_id)
    payload = json.dumps({"query": query, "variables": {}})

    for attempt in range(3):
        try:
            r = requests.post(GRAPHQL_URL, headers=HEADERS, data=payload, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                resp = r.json()
                if resp.get("errors"):
                    print(f"    [GQL ERR] {resp['errors'][0].get('message', '')}")
                    return [], False
                products = resp.get("data", {}).get("products") or [] 
                return products, True
            else:
                print(f"    [HTTP {r.status_code}]")
        except requests.RequestException as e:
            print(f"    [RETRY {attempt+1}] {e}")
            time.sleep(2 * (attempt + 1))

    return [], False

def crawl_province(province_id: int, writer, seen_ids: set, total_records: list) -> None:
    page         = 1
    empty_streak = 0

    while True:
        print(f"  [Trang {page:3d}] Đang tải... ", end="", flush=True)
        products, ok = fetch_page(page, PAGE_SIZE, province_id)

        if not ok:
            empty_streak += 1
            print(f"Lỗi ({empty_streak}/3)")
            if empty_streak >= 3:
                break
            time.sleep(5)
            page += 1
            continue

        if not products:
            empty_streak += 1
            print(f"Trống ({empty_streak}/3)")
            if empty_streak >= 3:
                break
            page += 1
            continue

        empty_streak = 0
        page_new = 0

        for prod in products:
            row = process_product(prod)
            if row is None: continue
            pid = str(row["product_id"])
            if pid in seen_ids: continue
            seen_ids.add(pid)
            writer.writerow(row)
            total_records[0] += 1
            page_new += 1

        writer._file_obj.flush()
        print(f"{len(products):3d} sp, {page_new:3d} mới | Tổng: {total_records[0]:5d}")

        if page_new == 0 and len(products) > 0:
            print(f"  [INFO] Hết sản phẩm mới (tất cả đã seen)")
            break

        page += 1
        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

def main():
    print("=" * 65)
    print(f"  CellphoneS Crawler v3 - GraphQL API (Multi-Province)")
    print(f"  URL: {GRAPHQL_URL}")
    print(f"  Category: {CATEGORY_ID} (Điện thoại)")
    print(f"  Page size: {PAGE_SIZE} | Provinces: {PROVINCES}")
    print("=" * 65)
    print()

    seen_ids      = set()
    total_records = [0]

    with open(OUTPUT_FILE, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer._file_obj = f
        writer.writeheader()

        for i, province_id in enumerate(PROVINCES, 1):
            print(f"\n[Tỉnh {i}/{len(PROVINCES)}] Province ID = {province_id}")
            print("-" * 50)
            crawl_province(province_id, writer, seen_ids, total_records)
            print(f"  -> Sau tỉnh #{i}: {total_records[0]} sản phẩm unique")

            if total_records[0] >= 1500:
                print(f"\n[DONE] Đã đạt {total_records[0]} sản phẩm, dừng lại.")
                break

    print(f"\n{'=' * 65}")
    print(f"  HOÀN THÀNH!")
    print(f"  Tổng sản phẩm unique: {total_records[0]}")
    print(f"  File đầu ra          : {OUTPUT_FILE}")
    print("=" * 65)

if __name__ == "__main__":
    main()
