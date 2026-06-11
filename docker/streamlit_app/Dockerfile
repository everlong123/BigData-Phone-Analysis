# Sử dụng Image Python chính thức, phiên bản thu gọn siêu nhẹ
FROM python:3.9-slim

# Thiết lập thư mục làm việc bên trong Container
WORKDIR /app

# Cài đặt các công cụ hệ thống cần thiết để build thư viện kết nối MySQL
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt trực tiếp các thư viện Python cần thiết cho Streamlit
RUN pip install --no-cache-dir \
    streamlit \
    mysql-connector-python \
    mysqlclient

# Mở cổng giao diện Streamlit
EXPOSE 8501