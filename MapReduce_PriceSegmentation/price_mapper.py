import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    
    parts = line.split(',')
    
    # Lệnh này sẽ chẻ tung cả dòng dữ liệu ra thành một mảng (danh sách)
    # ngay lập tức tại các vị trí có dấu phẩy.
    if len(parts) < 8:
        continue
        
    try:
        # Cột giá bán (sale_price) nằm ở vị trí thứ 8, tức là parts[7].
        price_str = parts[7].strip()
        
        # Loại bỏ tất cả các ký tự không phải số (dấu chấm, khoảng trắng)
        cleaned_price = ''.join(c for c in price_str if c.isdigit())
        
        # Nếu sau khi làm sạch mà không còn số nào (trường hợp dòng đó bị lỗi hoàn toàn), ta bỏ qua.
        if not cleaned_price:
            continue
            
        price = float(cleaned_price)
        
        # Segmentation logic based on your rules
        if price < 34000000:
            segment = "Budget"
        elif price <= 39000000:
            segment = "Mid-range"
        else:
            segment = "Premium"
            
        print(f"{segment}\t1")
        
    except (ValueError, IndexError):
        continue