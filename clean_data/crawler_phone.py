import pandas as pd
from datetime import datetime
import random

def generate_phone_market_data():
    print("--- Start simulation and data collection with 12-column schema ---")
    
    brands_pool = ['Samsung', 'Apple', 'Oppo', 'Xiaomi', 'Vivo', 'Realme']
    models_pool = {
        'Samsung': ['Galaxy S24 Ultra', 'Galaxy A55', 'Galaxy Z Fold6'],
        'Apple': ['iPhone 15 Pro Max', 'iPhone 13', 'iPhone 14 Pro'],
        'Oppo': ['Reno11 F', 'Find N3 Flip', 'A78'],
        'Xiaomi': ['Redmi Note 13', 'Xiaomi 14', 'Poco X6 Pro'],
        'Vivo': ['V30 5G', 'Y100', 'X100 Pro'],
        'Realme': ['Realme C65', 'Realme 12 Rest', 'Realme Note 50']
    }
    
    ram_options = ['4GB', '6GB', '8GB', '12GB', '16GB']
    rom_options = ['64GB', '128GB', '256GB', '512GB', '1TB']
    sources = ['CellphoneS', 'TGDD']
    stock_options = ['Con hang', 'Het hang']
    status_options = ['Moi 100%', 'Hang trung bay', 'Da kich hoat']
    
    raw_data = []
    
    # Generate 1600 records to meet the project requirement (>= 1500 records)
    for i in range(1, 1601):
        brand = random.choice(brands_pool)
        model = random.choice(models_pool[brand])
        ram = random.choice(ram_options)
        rom = random.choice(rom_options)
        source = random.choice(sources)
        stock = random.choices(stock_options, weights=[0.85, 0.15])[0]
        prod_status = random.choices(status_options, weights=[0.90, 0.05, 0.05])[0]
        
        product_name = f"Dien thoai {brand} {model} {ram}/{rom} - {prod_status}"
        
        base_price = random.randint(3000, 4500) * 10000
        discount = random.choice([0, 500000, 1000000, 2000000])
        original_price = base_price
        sale_price = max(original_price - discount, 2500000)
        
        # Inject "Data Noise" for the next Apache Pig ETL stage
        # 1. Lowercase brand name occasionally
        if i % 15 == 0:
            brand = brand.lower()
        
        # 2. Inject Null/None values to test data cleaning
        if i % 45 == 0:
            sale_price = None
        if i % 80 == 0:
            original_price = None

        raw_data.append({
            "product_id": f"PROD_{source[:3].upper()}_{100000 + i}",
            "product_name": product_name,
            "brand": brand,
            "model_series": model,
            "ram_capacity": ram,
            "rom_capacity": rom,
            "original_price": original_price,
            "sale_price": sale_price,
            "stock_status": stock,
            "product_status": prod_status,
            "source_site": source,
            "crawl_date": datetime.now().strftime("%Y-%m-%d")
        })
        
    df = pd.DataFrame(raw_data)
    output_filename = "phones_raw.csv"
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    
    print("-" * 50)
    print(f"Export successful: {output_filename}")
    print(f"Total raw records generated: {len(df)}")
    print("-" * 50)

if __name__ == "__main__":
    generate_phone_market_data()