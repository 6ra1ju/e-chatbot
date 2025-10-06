# Chatbot E-commerce Interface

## 🎯 Tổng quan

Đã tạo thành công giao diện chatbot cho ứng dụng e-commerce với các tính năng:

- ✅ **React Component**: Giao diện chat đẹp với streaming text
- ✅ **Django API**: Endpoint để kết nối với chatbot Python
- ✅ **Python Backend**: Script xử lý câu hỏi và trả về kết quả
- ✅ **Streaming Response**: Hiển thị text từng từ một cách mượt mà

## 📁 Cấu trúc Files

### Frontend (React)
```
client/src/components/
├── Chatbot.tsx          # Component chính của chatbot
├── Header.tsx           # Đã thêm link "Chatbot"
└── App.tsx              # Đã thêm route /chatbot
```

### Backend (Django)
```
server/shop/
├── views.py             # API endpoint chatbot_chat()
└── urls.py              # URL pattern /api/chatbot/chat/
```

### Python Scripts
```
chatbot/
├── simple_chatbot_api.py    # Script đơn giản (đang sử dụng)
├── chatbot_api.py           # Script phức tạp với AI
└── process_data.py          # Logic chatbot gốc
```

## 🚀 Cách sử dụng

### 1. Khởi động Django Server
```bash
cd /Users/raiju/Ecommerce-Web/server
python manage.py runserver
```

### 2. Khởi động React App
```bash
cd /Users/raiju/Ecommerce-Web/client
npm start
```

### 3. Truy cập Chatbot
- Mở trình duyệt: `http://localhost:3000`
- Click nút **"Chatbot"** (màu xanh lá) trên header
- Hoặc truy cập trực tiếp: `http://localhost:3000/chatbot`

## 💬 Các câu hỏi mẫu

### Tìm sản phẩm theo thương hiệu
- `gợi ý 3 sản phẩm từ brand vevor`
- `sản phẩm amazon basics`

### So sánh giá
- `sản phẩm đắt nhất`
- `sản phẩm rẻ nhất`

### Tìm theo khoảng giá
- `giá từ 100 đến 500`
- `sản phẩm giá từ 200 đến 1000`

## 🔧 Tính năng

### Frontend (Chatbot.tsx)
- ✅ **Giao diện chat đẹp** với Tailwind CSS
- ✅ **Streaming text** hiển thị từng từ
- ✅ **Quick suggestions** - các câu hỏi mẫu
- ✅ **Auto-scroll** xuống tin nhắn mới
- ✅ **Loading states** và error handling
- ✅ **Responsive design** cho mobile

### Backend (Django)
- ✅ **Streaming HTTP Response** với Server-Sent Events
- ✅ **CORS headers** để frontend kết nối được
- ✅ **Error handling** cho các trường hợp lỗi
- ✅ **Subprocess management** để chạy Python script

### Python Script (simple_chatbot_api.py)
- ✅ **Keyword-based responses** không cần AI phức tạp
- ✅ **Pandas data processing** để tìm kiếm sản phẩm
- ✅ **Multiple search strategies**:
  - Tìm theo thương hiệu
  - Tìm sản phẩm đắt nhất/rẻ nhất
  - Tìm theo khoảng giá
  - Tìm sản phẩm cụ thể

## 🎨 Giao diện

### Header
- **Home** (xanh dương) - Trang chủ
- **About** (trắng, viền xanh) - Giới thiệu  
- **Chatbot** (xanh lá) - Chat với AI

### Chat Interface
- **Messages area**: Hiển thị cuộc trò chuyện
- **Input area**: Nhập câu hỏi
- **Quick suggestions**: Các câu hỏi mẫu
- **Send button**: Gửi tin nhắn

## 🔄 Luồng hoạt động

1. **User** nhập câu hỏi vào React component
2. **React** gửi POST request đến Django API
3. **Django** khởi động Python script với câu hỏi
4. **Python script** xử lý và trả về kết quả
5. **Django** stream kết quả về React
6. **React** hiển thị text từng từ một cách mượt mà

## 🛠️ Troubleshooting

### Lỗi kết nối
- Kiểm tra Django server đang chạy trên port 8000
- Kiểm tra React app đang chạy trên port 3000
- Kiểm tra file `amazon_data.csv` có tồn tại

### Lỗi Python script
- Kiểm tra dependencies: `pandas`, `numpy`
- Kiểm tra file CSV có đúng format
- Kiểm tra quyền truy cập file

### Lỗi streaming
- Kiểm tra browser có hỗ trợ Server-Sent Events
- Kiểm tra network connection
- Kiểm tra CORS headers

## 📈 Cải tiến trong tương lai

- [ ] **AI Integration**: Sử dụng script `chatbot_api.py` với Groq API
- [ ] **Voice Input**: Thêm tính năng nhận diện giọng nói
- [ ] **File Upload**: Cho phép upload ảnh sản phẩm
- [ ] **Multi-language**: Hỗ trợ tiếng Anh
- [ ] **Chat History**: Lưu lịch sử chat
- [ ] **Product Links**: Thêm link đến sản phẩm cụ thể

## 🎉 Kết luận

Chatbot đã được tích hợp thành công vào ứng dụng e-commerce với:
- Giao diện đẹp và thân thiện
- Streaming text mượt mà
- Xử lý câu hỏi thông minh
- Kết nối ổn định giữa frontend và backend

**Sẵn sàng sử dụng!** 🚀
