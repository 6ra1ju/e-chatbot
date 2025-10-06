#!/usr/bin/env python3
"""
Simple Chatbot Server - Keeps models loaded in memory
Run this server once, then Django can call it via HTTP
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
import os
from pathlib import Path


current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print("🚀 Initializing chatbot...")
from process_data import (
    df_global, load_and_clean_data, connect_milvus_lite,
    get_highest_price, get_lowest_price, product_from_brand,
    suggest_by_price, recommend_product_by_range, product_same_brand,
    HuggingFaceEmbeddings, ChatGroq, create_react_agent,
    HumanMessage, EMBEDDING_MODEL
)
import process_data
import pandas as pd
from langchain.tools import tool

# Load data
if process_data.df_global is None:
    csv_path = "amazon_data.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError("amazon_data.csv not found")
    process_data.df_global = load_and_clean_data(csv_path)
    print("✅ Data loaded")

connect_milvus_lite()
print("✅ Connected to Milvus")


llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0,
)
print("✅ LLM initialized")

@tool
def search_text(q: str) -> str:
    """Search for product information by name, brand, features, description, size, rating, or price.
    Use this when user asks about specific product details like:
    - "thông tin về sản phẩm X" / "info about product X"
    - "brand của sản phẩm X" / "brand of product X"  
    - "feature của sản phẩm X" / "features of product X"
    - "giá của sản phẩm X" / "price of product X"
    - "mô tả sản phẩm X" / "description of product X"
    - "rating của sản phẩm X" / "rating of product X"
    - "size của sản phẩm X" / "size of product X"
    """
    try:
        import re
        
        # STEP 1: Detect what field user is asking for (BEFORE extracting product name)
        # Use ordered list to prioritize specific keywords (rating, price first)
        requested_field = None
        field_mappings = [
            ('rating', 'rating'),
            ('đánh giá', 'rating'),
            
            ('price', 'salePrice'),
            ('giá', 'salePrice'),
            
            ('features', 'features'),
            ('đặc điểm', 'features'),
            
            ('description', 'description'),
            ('mô tả', 'description'),
            
            ('brand', 'brandName'),
            ('thương hiệu', 'brandName'),
            
            ('size', 'size'),
            ('kích thước', 'size'),
            
            ('material', 'material'),
            ('chất liệu', 'material'),
        ]
        
        for keyword, field in field_mappings:
            pattern = rf'\b{re.escape(keyword)}\b'
            if re.search(pattern, q.lower()):
                requested_field = field
                print(f"🔍 Detected field request: {keyword} → {field}")
                break
        
        # STEP 2: Extract product name from query
        product_name = q
        
        if requested_field:
            for keyword, field in field_mappings:
                if field == requested_field and keyword in q.lower():
                    product_name = re.sub(rf'\b{re.escape(keyword)}\b', '', product_name, flags=re.IGNORECASE).strip()
                    print(f"🔧 Removed keyword '{keyword}' from query")
                    break
        
        product_name = re.sub(r'\bcủa\b', '', product_name, flags=re.IGNORECASE).strip()
        product_name = re.sub(r'\bsản phẩm\b', '', product_name, flags=re.IGNORECASE).strip()
        
        product_name = product_name.replace('"', '').replace("'", "").strip()
        
        if not product_name or len(product_name) < 3:
            return "❌ Tên sản phẩm quá ngắn. Vui lòng cung cấp tên sản phẩm rõ ràng hơn."
        
        mask = process_data.df_global["name"].str.contains(product_name, case=False, na=False, regex=False)
        matching_products = process_data.df_global[mask]
        
        if matching_products.empty:
            words = product_name.split()[:3]
            if words:
                search_term = ' '.join(words)
                mask = process_data.df_global["name"].str.contains(search_term, case=False, na=False, regex=False)
                matching_products = process_data.df_global[mask]
        
        if matching_products.empty:
            first_word = product_name.split()[0] if product_name.split() else ""
            if first_word and len(first_word) > 2:
                mask = process_data.df_global["name"].str.contains(first_word, case=False, na=False, regex=False)
                matching_products = process_data.df_global[mask]
        
        if matching_products.empty:
            return f"❌ Không tìm thấy sản phẩm '{product_name}' trong cơ sở dữ liệu."
        
        product = matching_products.iloc[0]
        print(f"✅ Found product: {product.get('name', 'N/A')[:50]}...")
        
        if requested_field and requested_field in product and pd.notna(product[requested_field]):
            field_labels = {
                "material": "Chất liệu",
                "features": "Đặc điểm",
                "description": "Mô tả",
                "salePrice": "Giá bán",
                "rating": "Đánh giá",
                "brandName": "Thương hiệu",
                "size": "Kích thước",
            }
            
            label = field_labels.get(requested_field, requested_field)
            value = str(product[requested_field])
            
            value = re.sub(r'[\\{}\[\]"]', '', value).strip()
            value = re.sub(r'\s+', ' ', value)
            
            if len(value) > 500:
                value = value[:500] + "..."
            
            return f"{label} của sản phẩm '{product.get('name', 'N/A')}': {value}"
        
        result = f"🔍 Thông tin sản phẩm: {product.get('name', 'N/A')}\n"
        
        field_map = {
            "brandName": "Thương hiệu",
            "salePrice": "Giá bán",
            "rating": "Đánh giá",
            "material": "Chất liệu",
            "size": "Kích thước",
        }
        
        for col, label in field_map.items():
            if col in product and pd.notna(product[col]):
                value = str(product[col])
                value = re.sub(r'[\\{}\[\]"]', '', value).strip()
                value = re.sub(r'\s+', ' ', value)
                if len(value) > 200:
                    value = value[:200] + "..."
                result += f"{label}: {value}\n"
        
        return result
        
    except Exception as e:
        return f"❌ Lỗi khi tìm kiếm: {str(e)}"

print("✅ search_text tool created")

tools = [
    get_highest_price,
    get_lowest_price,
    suggest_by_price,
    recommend_product_by_range,
    product_from_brand,
    product_same_brand,
    search_text,
]

system_prompt = """You are a helpful Vietnamese e-commerce assistant. 

CRITICAL TOOL SELECTION RULES:

1. PRICE RANGE queries (từ X đến Y, between X and Y):
   → Use recommend_product_by_range(q=query, field="salePrice", n=3, min_price=X, max_price=Y)
   
2. HIGHEST/MOST EXPENSIVE (đắt nhất, cao nhất):
   → Use get_highest_price(field="salePrice")
   
3. LOWEST/CHEAPEST (rẻ nhất, thấp nhất):
   → Use get_lowest_price(field="salePrice")
   
4. BRAND queries (sản phẩm VEVOR, products from X):
   → Use product_from_brand(brand_name="X", n=3)
   
5. NEAR A PRICE (gần giá X, around price X):
   → Use suggest_by_price(q=query, field="salePrice", n=3, ref_price=X)

EXAMPLES:
- "sản phẩm có giá từ 100 đến 500" → recommend_product_by_range
- "sản phẩm đắt nhất" → get_highest_price
- "sản phẩm VEVOR" → product_from_brand
- "sản phẩm gần 200" → suggest_by_price
- "brand của sản phẩm rẻ nhất" → suggest_lowest_price
- "feature/size/description của sản phẩm X" → search_text
- "rating của sản phẩm X" → suggest_text
- "sản phẩm có rating 4.5" → suggest_text
- "sản phẩm có size L" → suggest_text
- "sản phẩm có description X" → search_text
- "giá của sản phẩm X" → search_text


IMPORTANT: 
- Always use field="salePrice" 
- Pass the full original query as 'q' parameter"""

agent_executor = create_react_agent(llm, tools, prompt=system_prompt)
print("✅ Agent ready")
print("\n🎉 Chatbot server is ready! Listening on port 8001...")

class ChatbotHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                message = data.get('message', '')
                
                if not message:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Message required'}).encode())
                    return
                
                print(f"\n📨 Received: {message}")
                
                # Process with LLM agent
                tool_result = None
                config = {"recursion_limit": 10}
                
                for chunk in agent_executor.stream({"messages": [HumanMessage(content=message)]}, config=config):
                    if "tools" in chunk and "messages" in chunk["tools"]:
                        for msg in chunk["tools"]["messages"]:
                            if hasattr(msg, "content") and msg.content:
                                tool_result = msg.content
                                break
                
                response_text = tool_result if tool_result else "Xin lỗi, tôi không thể xử lý câu hỏi này."
                print(f"✅ Response: {response_text[:100]}...")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'response': response_text}).encode())
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8001), ChatbotHandler)
    server.serve_forever()

