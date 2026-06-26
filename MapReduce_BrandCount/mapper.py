#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.strip() # Biến cái "CPS_123, iPhone 15 Pro, Apple, 8GB, 256GB\n" thành "CPS_123, iPhone 15 Pro, Apple, 8GB, 256GB"
    if not line:
        continue
        
    # Find the first comma (end of Product_ID)
    first_comma = line.find(',')
    if first_comma == -1:
        continue
        
    # Find the second comma (end of Product_Name)
    # This correctly skips any text inside Product_Name
    second_comma = line.find(',', first_comma + 1)
    if second_comma == -1:
        continue
        
    # Find the third comma (end of Brand)
    third_comma = line.find(',', second_comma + 1)
    if third_comma == -1:
        # If there is no third comma, the rest of the line is the Brand
        brand = line[(second_comma + 1):].strip()
    else:
        brand = line[(second_comma + 1):third_comma].strip()
        
    if brand:
        # Standard Output with clear tab separation
        sys.stdout.write(f"{brand}\t1\n")

# {brand}: Sẽ được thay bằng tên hãng (Ví dụ: Apple, Samsung).
# \t: Đây là phím Tab trên bàn phím. Nó sẽ tạo ra một khoảng trắng dài (thường bằng 4 hoặc 8 dấu cách) để đẩy số 1 cách xa tên hãng ra cho dễ nhìn.
# 1: Con số 1 tượng trưng cho "1 cái điện thoại".
# \n: Ký tự Enter xuống dòng. Do write() không tự xuống dòng, nên ta phải ép nó xuống dòng sau khi in xong, để dành chỗ cho cái điện thoại tiếp theo.

# Apple   1
# Samsung 1
# Apple   1
# Xiaomi  1
# Oppo    1
