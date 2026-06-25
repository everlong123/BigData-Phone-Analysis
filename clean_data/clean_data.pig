RAW_DATA = LOAD '/bigdata/phone_analysis/input/phones_raw.csv' USING PigStorage(',') AS (
    product_id: chararray,
    product_name: chararray,
    brand: chararray,
    model_series: chararray,
    ram_capacity: chararray,
    rom_capacity: chararray,
    original_price: chararray,
    sale_price: chararray,
    stock_status: chararray,
    product_status: chararray,
    source_site: chararray,
    crawl_date: chararray
);

FILTERED_HEADER = FILTER RAW_DATA BY product_id != 'product_id' AND product_id != '"product_id"';

CASTED_DATA = FOREACH FILTERED_HEADER GENERATE 
    product_id, product_name, brand, model_series, ram_capacity, rom_capacity,
    (long)original_price AS original_price,
    (long)sale_price AS sale_price,
    stock_status, product_status, source_site, crawl_date;

CLEANED_NULL = FILTER CASTED_DATA BY (original_price IS NOT NULL) AND (sale_price IS NOT NULL);

LOWER_BRAND = FOREACH CLEANED_NULL GENERATE 
    product_id, product_name, 
    LOWER(TRIM(brand)) AS brand_lower,
    model_series, ram_capacity, rom_capacity, original_price, sale_price, stock_status, product_status, source_site, crawl_date;

STANDARDIZED_DATA = FOREACH LOWER_BRAND GENERATE 
    product_id,
    product_name,
    ((brand_lower == 'samsung') ? 'Samsung' : 
     ((brand_lower == 'apple') ? 'Apple' : 
      ((brand_lower == 'oppo') ? 'Oppo' : 
       ((brand_lower == 'xiaomi') ? 'Xiaomi' : 
        ((brand_lower == 'vivo') ? 'Vivo' : 
         ((brand_lower == 'realme') ? 'Realme' : brand_lower)))))) AS brand,
    model_series,
    ram_capacity,
    rom_capacity,
    original_price,
    sale_price,
    stock_status,
    product_status,
    source_site,
    crawl_date;

FINAL_CLEANED_DATA = DISTINCT STANDARDIZED_DATA;

STORE FINAL_CLEANED_DATA INTO '/bigdata/phone_analysis/output' USING PigStorage(',');