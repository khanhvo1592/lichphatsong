# Sử dụng base image từ Python 3
FROM python:3.8-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép file yêu cầu và cài đặt các gói cần thiết
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép tất cả các file còn lại vào container
COPY . .

# Mở cổng 5000
EXPOSE 5000

# Chạy ứng dụng Flask
CMD ["python", "./app.py"]
