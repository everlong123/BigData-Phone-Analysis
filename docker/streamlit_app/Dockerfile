FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    streamlit \
    pandas \
    numpy \
    plotly \
    sqlalchemy \
    pymysql \
    mysql-connector-python \
    mysqlclient

EXPOSE 8501