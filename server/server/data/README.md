# Data Processing Scripts

Thư mục này chứa các script để xử lý dữ liệu và cập nhật database.

## 📁 Files

- **`data-e.csv`**: File CSV gốc chứa dữ liệu bán hàng (43MB)
- **`processed_products.json`**: Dữ liệu đã xử lý (4.6MB, 1000 sản phẩm)
- **`process_data.py`**: Script xử lý CSV và tạo JSON
- **`update_database.py`**: Script cập nhật database từ JSON
- **`update_discounts.py`**: Script cập nhật discount cho sản phẩm

## 🚀 Cách sử dụng

### 1. Xử lý dữ liệu CSV
```bash
cd server/server/data
python3 process_data.py
```

**Chức năng:**
- Đọc `data-e.csv` với encoding latin-1
- Group by StockCode, Description, UnitPrice
- Filter bỏ descriptions chứa "check"
- Lấy 1000 samples đầu tiên
- Transform thành format sản phẩm
- Lưu vào `processed_products.json`

### 2. Cập nhật database
```bash
cd server/server/data
python3 update_database.py
```

**Chức năng:**
- Xóa tất cả products hiện tại
- Tạo products mới từ `processed_products.json`
- Hiển thị thống kê và sample

### 3. Cập nhật discount
```bash
cd server/server/data
python3 update_discounts.py
```

**Chức năng:**
- Cập nhật discount cho tất cả products
- Phân phối discount từ 10-30% với step 1
- Sử dụng product.id để đảm bảo consistency
- Hiển thị thống kê phân phối

## 📊 Quy trình hoàn chỉnh

```bash
# 1. Xử lý dữ liệu
python3 process_data.py

# 2. Cập nhật database
python3 update_database.py

# 3. Cập nhật discount
python3 update_discounts.py
```

## 📈 Kết quả

- **1000 sản phẩm** trong database
- **Discount**: 10-30% với phân phối đều
- **Images**: Tự động assign từ assets
- **Labels**: ["food", "vietnamese"] mặc định

## 🔧 Lưu ý

- Đảm bảo Django server đã được setup
- Chạy từ thư mục `server/server/data`
- Backup database trước khi chạy update scripts
- Kiểm tra logs để đảm bảo không có lỗi
