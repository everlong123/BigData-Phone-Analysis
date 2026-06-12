-- 1. Load raw data du?i d?ng chararray d? b?o v? dòng Header và tránh l?i ép ki?u s?m
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

-- 2. Lo?i b? hoàn toàn dòng tiêu d? (Header) kh?i d? li?u
FILTERED_HEADER = FILTER RAW_DATA BY product_id != 'product_id' AND product_id != '"product_id"';

-- 3. Ép ki?u an toàn sang s? LONG và l?c b? các b?n ghi l?i ho?c tr?ng (NULL)
CASTED_DATA = FOREACH FILTERED_HEADER GENERATE 
    product_id, product_name, brand, model_series, ram_capacity, rom_capacity,
    (long)original_price AS original_price,
    (long)sale_price AS sale_price,
    stock_status, product_status, source_site, crawl_date;

CLEANED_NULL = FILTER CASTED_DATA BY (original_price IS NOT NULL) AND (sale_price IS NOT NULL);

-- 4. T?i uu hóa chu?n hóa: Chuy?n toàn b? tên thuong hi?u v? ch? thu?ng tru?c d? x? lý mu?t mà
LOWER_BRAND = FOREACH CLEANED_NULL GENERATE 
    product_id, product_name, 
    LOWER(TRIM(brand)) AS brand_lower,
    model_series, ram_capacity, rom_capacity, original_price, sale_price, stock_status, product_status, source_site, crawl_date;

-- S? d?ng c?u trúc r? nhánh ph?ng, tránh l?ng sâu gây l?i "state DEFINE"
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

-- 5. L?c trùng l?p nâng cao (Deduplication) d? d?m b?o tính duy nh?t
FINAL_CLEANED_DATA = DISTINCT STANDARDIZED_DATA;

-- 6. Ghi tr?c ti?p k?t qu? s?ch ra thu m?c Output c?a HDFS
STORE FINAL_CLEANED_DATA INTO '/bigdata/phone_analysis/output' USING PigStorage(',');