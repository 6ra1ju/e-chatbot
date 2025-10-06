# E-commerce Application

Ứng dụng e-commerce với React frontend, Django backend, và AI Chatbot.

## Cấu trúc dự án

```
Ecommerce-Web/
├── client/          # React frontend
├── server/          # Django backend
├── chatbot/         # AI Chatbot (LLM + Vector Search)
└── venv/           # Python virtual environment
```

## Cài đặt và chạy

### Backend (Django)

1. **Cài đặt dependencies:**
```bash
cd server
pip3 install -r requirements.txt
```

2. **Chạy migrations:**
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

3. **Populate dữ liệu mẫu:**
```bash
python3 manage.py populate_products
```

4. **Khởi động server:**
```bash
python3 manage.py runserver
```

Server sẽ chạy tại `http://127.0.0.1:8000/`

### Frontend (React)

1. **Cài đặt dependencies:**
```bash
cd client
npm install
```

2. **Khởi động development server:**
```bash
npm start
```

Frontend sẽ chạy tại `http://localhost:3000/`

### Chatbot (AI)

**Xem hướng dẫn chi tiết tại [`chatbot/README.md`](chatbot/README.md)**

1. **Cài đặt dependencies:**
```bash
cd chatbot
pip install -r requirements.txt
```

2. **Tạo file `.env`:**
```env
GROQ_API_KEY=your_groq_api_key_here
```

3. **Ingest data (lần đầu tiên):**
```bash
python3 ai.py ingest
```

4. **Khởi động chatbot server:**
```bash
python3 simple_chatbot_server.py
```

Chatbot server sẽ chạy tại `http://localhost:8001/`

## API Endpoints

### Products
- `GET /api/products/` - Lấy tất cả sản phẩm
- `GET /api/products/{id}/` - Lấy sản phẩm theo ID
- `POST /api/products/create/` - Tạo sản phẩm mới

### Chatbot
- `POST /api/chatbot/chat/` - Chat với AI chatbot

### Admin
- `GET /admin/` - Django Admin interface

## Tính năng

### Frontend
- Hiển thị danh sách sản phẩm
- Thêm sản phẩm vào giỏ hàng
- Quản lý số lượng sản phẩm trong giỏ
- Xóa sản phẩm khỏi giỏ hàng
- Xóa toàn bộ giỏ hàng
- Trang checkout với thanh toán
- Responsive design
- **AI Chatbot** - Floating widget với streaming response

### Backend
- REST API với Django REST Framework
- Model Product với đầy đủ thông tin
- Django Admin để quản lý dữ liệu
- CORS headers cho frontend integration
- Management commands để populate data
- **Chatbot API** - Integration with AI chatbot server

### Chatbot (AI)
- **Natural Language Processing** - Vietnamese & English
- **Price Queries** - Range, highest, lowest
- **Brand Search** - Find products by brand
- **Product Info** - Features, rating, size, etc.
- **Vector Search** - Milvus for semantic search
- **Fast Response** - Optimized preprocessing (~0.1s)
- **LLM Agent** - Groq (llama-3.1-8b-instant)

## Kết nối Frontend-Backend

Frontend sẽ tự động fetch data từ Django API tại `http://127.0.0.1:8000/api/products/`. Nếu API không khả dụng, frontend sẽ fallback về mock data.

## Database

Sử dụng SQLite3 với các bảng:
- `products` - Thông tin sản phẩm
- Django default tables (admin, auth, etc.)

## Kết nối Frontend-Backend-Chatbot

```
┌──────────────────┐
│  React Frontend  │ (Port 3000)
│  - Product List  │
│  - Shopping Cart │
│  - Chatbot UI    │
└────────┬─────────┘
         │ HTTP API
         ▼
┌──────────────────┐
│  Django Backend  │ (Port 8000)
│  - Products API  │
│  - Chatbot API   │
│  - Admin Panel   │
└────────┬─────────┘
         │ HTTP Call
         ▼
┌──────────────────┐
│  Chatbot Server  │ (Port 8001)
│  - LLM Agent     │
│  - Vector Search │
│  - 7 AI Tools    │
└──────────────────┘
```

## Tech Stack

### Frontend
- React 18 + TypeScript
- Tailwind CSS
- React Router
- Fetch API

### Backend
- Django 4.2.7
- Django REST Framework 3.14.0
- SQLite3

### Chatbot
- LangChain + LangGraph
- Groq (LLM: llama-3.1-8b-instant)
- Milvus Lite (Vector Database)
- HuggingFace Embeddings
- Pandas + DuckDB

## Quick Start

**Tổng quan để chạy full stack:**

1. **Terminal 1 - Django Backend:**
```bash
cd server
python3 manage.py runserver
```

2. **Terminal 2 - Chatbot Server:**
```bash
cd chatbot
python3 simple_chatbot_server.py
```

3. **Terminal 3 - React Frontend:**
```bash
cd client
npm start
```

Truy cập: http://localhost:3000

## Example Queries (Chatbot)

- "sản phẩm đắt nhất"
- "sản phẩm rẻ nhất"
- "sản phẩm có giá từ 100 đến 500"
- "sản phẩm VEVOR"
- "brand của sản phẩm Amazon Basics"
- "rating của sản phẩm UFO SUKIT407-001"
- "feature của sản phẩm Sony WH-1000XM4"

## License

MIT License