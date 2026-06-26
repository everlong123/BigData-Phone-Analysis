#Giữa bước Mapper và Reducer, Hadoop đã âm thầm làm một việc gọi là "Shuffle & Sort". 
# Nó tự động sắp xếp tất cả các Key theo thứ tự chữ cái (A-Z). 
# Vì vậy, dữ liệu mà reducer.py chuẩn bị đọc vào sẽ trông cực kỳ ngăn nắp thế này:

# Apple   1
# Apple   1
# Apple   1
# Oppo    1
# Oppo    1
# Samsung 1
# Samsung 1



#!/usr/bin/env python3
import sys

current_brand = None
current_count = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
        
    #if '\t' not in line: Một chốt chặn an toàn nữa. Nếu dòng dữ liệu mà không có dấu Tab (\t) nào cả, thì chứng tỏ dòng đó bị lỗi định dạng (không phải cấu trúc Key \t Value), lập tức vứt đi để không văng lỗi.
    if '\t' not in line:
        continue
        
    # line.split('\t', 1): Đây là chiêu bửa củi. Dùng cái rìu là dấu Tab (\t), bổ đôi dòng chữ ra làm 2 khúc.
    # Khúc bên trái dấu Tab ném vào biến brand (Ví dụ: "Apple").
    # Khúc bên phải dấu Tab ném vào biến count (Ví dụ: "1").
    brand, count = line.split('\t', 1)
    
    try:
        count = int(count) #Mặc dù số 1 nhìn là số, nhưng với máy tính lúc này nó vẫn là chữ "1". Ta phải ép nó về số nguyên
    except ValueError:
        continue

    if current_brand == brand:
        current_count += count
    else:
        if current_brand:
            sys.stdout.write(f"{current_brand}\t{current_count}\n")
        current_brand = brand
        current_count = count

if current_brand:
    sys.stdout.write(f"{current_brand}\t{current_count}\n")