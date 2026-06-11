
## Yêu cầu

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) đã cài và đang chạy
- Không cần cài Python, MySQL hay bất kỳ thứ gì khác

---

## Cấu trúc thư mục

```
project/
├── docker-compose.yml
├── superset_config.py
└── streamlit_app/
    └── app.py
```

---

## Chạy lần đầu

```bash
# 1. Vào thư mục project
cd đường/dẫn/tới/project

# 2. Khởi động toàn bộ stack
docker-compose up -d
```

Lần đầu tải image mất khoảng **3–5 phút**. Chờ xong rồi kiểm tra:

```bash
docker-compose ps
```

Kết quả mong đợi — cả 3 service đều `running`:

```
NAME                 STATUS
bigdata_mysql        running (healthy)
bigdata_superset     running
bigdata_streamlit    running
```

---

## Truy cập giao diện

| Service   | URL                   | Tài khoản                    |
|-----------|-----------------------|------------------------------|
| Streamlit | http://localhost:8501 | không cần login              |
| Superset  | http://localhost:8088 | admin / admin123             |
| MySQL     | localhost:3306        | bigdata_user / bigdata_pass  |

---

## Test nhanh (chưa có data từ TV2)

Tạo bảng và nhét vài dòng mẫu để Streamlit có gì hiển thị:

```bash
docker exec -i bigdata_mysql mysql -u bigdata_user -pbigdata_pass phones_db << 'EOF'
CREATE TABLE IF NOT EXISTS phones (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(255),
  brand      VARCHAR(100),
  ram        INT,
  rom        INT,
  price      BIGINT,
  source     VARCHAR(50),
  crawl_date DATE DEFAULT (CURRENT_DATE)
);

INSERT INTO phones (name, brand, ram, rom, price, source) VALUES
  ('iPhone 15 Pro',      'Apple',   8,  256, 28990000, 'CellphoneS'),
  ('Samsung Galaxy S24', 'Samsung', 12, 256, 22990000, 'TGDD'),
  ('Xiaomi 14',          'Xiaomi',  12, 512, 17990000, 'CellphoneS'),
  ('OPPO Find X7',       'OPPO',    16, 512, 19990000, 'TGDD'),
  ('Vivo X100',          'Vivo',    12, 256, 15990000, 'CellphoneS');
EOF
```

Sau đó vào **http://localhost:8501** — data sẽ hiện ngay.

---

## Khi có data thật từ TV2

```bash
# Copy file SQL vào thư mục project, rồi chạy 1 lệnh:
docker exec -i bigdata_mysql mysql -u bigdata_user -pbigdata_pass phones_db < phones_database.sql
```

Không cần restart, Streamlit tự đọc data mới.

---

## Kết nối Superset vào MySQL

1. Vào **http://localhost:8088** → đăng nhập `admin / admin123`
2. Menu trên: **Settings → Database Connections → + Database**
3. Chọn **MySQL**, dán URI sau vào ô SQLAlchemy:

```
mysql+mysqlconnector://bigdata_user:bigdata_pass@mysql:3306/phones_db
```

> ⚠️ Dùng hostname `mysql` (tên service trong docker-compose), **không phải** `localhost`

4. Bấm **Test Connection** → **Connect**
5. **Datasets → + Dataset** → chọn bảng `phones` → **Create Dataset**
6. **Charts** → tạo từng biểu đồ (Bar, Pie, Line, KPI...) từ dataset
7. **Dashboards** → gom các chart thành 1 dashboard hoàn chỉnh

---

## Xem log khi có lỗi

```bash
docker-compose logs -f streamlit
docker-compose logs -f superset
docker-compose logs -f mysql
```

---

## Các lệnh thường dùng

```bash
# Dừng (giữ nguyên data)
docker-compose down

# Dừng + xóa hết data (reset hoàn toàn)
docker-compose down -v

# Restart 1 service
docker-compose restart streamlit

# Vào MySQL chạy SQL tay
docker exec -it bigdata_mysql mysql -u bigdata_user -pbigdata_pass phones_db
```



