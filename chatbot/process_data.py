
import os
import re
import duckdb
import pandas as pd

from typing import Literal
from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.chains import ConversationalRetrievalChain
from langchain.tools import tool, StructuredTool
from langchain.agents import initialize_agent, AgentType, Tool, AgentExecutor
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_milvus import Milvus
from pymilvus import connections
from langchain_core.messages import SystemMessage
from langchain.prompts import ChatPromptTemplate

load_dotenv()
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

COLLECTION_NAME = "test"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MILVUS_URI = "milvus_lite.db"
DATA_PATH = "amazon_data.csv"


def load_and_clean_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.replace(r"[^0-9a-zA-Z_]", "_", regex=True)

    required_cols = [
        "additionalProperties", "brandName", "breadcrumbs", "color", "currency",
        "current_depth", "description", "descriptionRaw", "features", "imageUrls",
        "inStock", "listedPrice", "material", "name", "new_path", "nodeName",
        "rating", "reviewCount", "salePrice", "size", "style", "variants",
        "weight_rawUnit", "weight_unit", "weight_value"
    ]

    df_clean = df.dropna(subset=[c for c in required_cols if c in df.columns])
    df_clean = df_clean[
        [
            "additionalProperties", "brandName", "breadcrumbs", "description",
            "descriptionRaw", "features", "salePrice", "material", "name",
            "rating", "size", "style"
        ]
    ]
    return df_clean


def df_to_documents(df: pd.DataFrame, text_columns=None):
    docs = []
    for _, row in df.iterrows():
        if text_columns:
            content = " ".join(str(row.get(col, "")) for col in text_columns)
        else:
            content = " ".join(str(v) for v in row.values)

        metadata = {k: str(v) for k, v in row.to_dict().items()}
        docs.append(Document(page_content=content, metadata=metadata))
    return docs


def connect_milvus_lite():
    try:
        if connections.has_connection("default"):
            return
        connections.connect(alias="default", uri=MILVUS_URI)
    except Exception as e:
        try:
            connections.disconnect("default")
        except:
            pass
        connections.connect(alias="default", uri=MILVUS_URI)


def chunk_documents(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    return splitter.split_documents(docs)


def ingest(folder: str):
    connect_milvus_lite()
    csv_path = DATA_PATH
    if not os.path.exists(csv_path):
        csv_path = "amazon_data.csv"
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"❌ Không tìm thấy file: {csv_path}")

    df_clean = load_and_clean_data(str(csv_path))
    docs = df_to_documents(
        df_clean,
        text_columns=[
            "additionalProperties", "brandName", "breadcrumbs",
            "description", "descriptionRaw", "features", "salePrice",
            "material", "name", "rating", "size", "style"
        ],
    )
    chunks = chunk_documents(docs)
    embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    Milvus.from_documents(
        chunks,
        embedding,
        collection_name=COLLECTION_NAME,
        connection_args={"uri": MILVUS_URI},
    )
    print("✅ Ingested", len(chunks), "chunks vào Milvus Lite.")


df_global = None

session_state = {
    "last_product_idx": None,
    "last_field": None,
}


def _clean_price(series):
    return pd.to_numeric(series, errors="coerce").dropna()


def _get_unique_products(df_global, idxs, field, n):
    """Get N unique products by name, removing duplicates."""
    seen_names = set()
    unique_idxs = []
    
    for idx in idxs:
        name = df_global.loc[idx].get('name', '')
        if name and name not in seen_names:
            seen_names.add(name)
            unique_idxs.append(idx)
            if len(unique_idxs) >= n:
                break
    
    return unique_idxs


@tool
def get_highest_price(field: Literal["listedPrice", "salePrice"] = "salePrice") -> str:
    """Find and return the product with the highest price, including brand information.
    Use this when user asks about the most expensive product, highest price, or đắt nhất.
    This tool returns complete product info including brand name.
    field: 'salePrice' for final price, 'listedPrice' for original price."""
    global df_global
    prices = _clean_price(df_global[field])
    if prices.empty:
        return f"❌ Không tìm thấy dữ liệu trong {field}."

    idx = prices.idxmax()
    row = df_global.loc[idx]
    session_state["last_product_idx"] = idx
    session_state["last_field"] = field

    currency = row.get('currency', 'USD')
    brand = row.get('brandName', 'N/A')
    name = row.get('name', 'N/A')
    price = row.get(field, 0)
    
    return f"Sản phẩm đắt nhất theo {field} là '{name}' từ thương hiệu '{brand}' với giá {price} {currency}."


@tool
def get_lowest_price(field: Literal["listedPrice", "salePrice"] = "salePrice") -> str:
    """Find and return the product with the lowest price, including brand information.
    Use this when user asks about the cheapest product, lowest price, or rẻ nhất.
    This tool returns complete product info including brand name.
    field: 'salePrice' for final price, 'listedPrice' for original price."""
    global df_global
    prices = _clean_price(df_global[field])
    if prices.empty:
        return f"❌ Không tìm thấy dữ liệu trong {field}."

    idx = prices.idxmin()
    row = df_global.loc[idx]
    session_state["last_product_idx"] = idx
    session_state["last_field"] = field

    currency = row.get('currency', 'USD')
    brand = row.get('brandName', 'N/A')
    name = row.get('name', 'N/A')
    price = row.get(field, 0)
    
    return f"Sản phẩm rẻ nhất theo {field} là '{name}' từ thương hiệu '{brand}' với giá {price} {currency}."

@tool()
def suggest_by_price(q: str, field: Literal["listedPrice", "salePrice"] = "salePrice", n: int = 1, ref_price: float = None) -> str:
    """Find N products with price CLOSE TO a specific reference price.
    
    Use this when user asks for products NEAR a specific price:
    - "gợi ý sản phẩm gần giá X"
    - "suggest products near price X" 
    - "tìm sản phẩm tương tự giá X"
    - "closest to price X"
    
    This finds products with prices closest to the reference price (not in a range).
    
    Args:
        q: User query
        field: 'salePrice' for final price, 'listedPrice' for original price
        n: Number of products to return (default 1)
        ref_price: Reference price to find closest matches to
    """

    global df_global
    if (
        ref_price is None 
        and ("món này" in q or "mon nay" in q) 
        and session_state.get("last_product_idx") is not None
    ):
        ref_idx = session_state["last_product_idx"]
        ref_field = session_state.get("last_field") or field
        try:
            ref_price = float(df_global.loc[ref_idx, ref_field])
            field = ref_field
        except Exception:
            ref_price = None
    if ref_price is None:
        return "❌ Chưa có giá tham chiếu. Hãy nêu rõ một mức giá hoặc hỏi dựa trên 'món này'."
    prices = pd.to_numeric(df_global[field], errors='coerce')
    diffs = (prices - ref_price).abs()
    order = diffs.sort_values().index

    all_idxs = list(order)
    unique_idxs = _get_unique_products(df_global, all_idxs, field, n)
    
    if not unique_idxs:
        return "❌ Không tìm thấy sản phẩm phù hợp."

    lines = []
    for idx in unique_idxs:
        r = df_global.loc[idx]
        currency = r.get('currency', 'USD')
        lines.append(f"- {r.get('name','')} ({r.get(field)} {currency})")

    session_state["last_product_idx"] = unique_idxs[0]
    session_state["last_field"] = field

    return f"Gợi ý {len(unique_idxs)} sản phẩm gần {ref_price} ({field}):\n" + "\n".join(lines)

@tool
def recommend_product_by_range(q: str, field: Literal["listedPrice", "salePrice"] = "salePrice", n: int = 3, min_price: float = 0, max_price: float = None) -> str:
    """Find N products with price WITHIN a specific range (min to max).
    
    Use this when user asks for products in a PRICE RANGE:
    - "sản phẩm từ X đến Y"
    - "products between X and Y"
    - "sản phẩm trong khoảng X-Y"
    - "recommend products in range X to Y"
    - "tìm sản phẩm giá từ X đến Y"
    
    This finds products with prices between min_price and max_price.
    
    Args:
        q: User query
        field: 'salePrice' for final price, 'listedPrice' for original price
        n: Number of products to return (default 3)
        min_price: Minimum price of the range
        max_price: Maximum price of the range
    """

    global df_global
    if max_price is None:
        return "❌ Chưa có giá tham chiếu. Hãy nêu rõ một mức giá hoặc hỏi dựa trên 'món này'."
    prices = pd.to_numeric(df_global[field], errors='coerce')
    filtered = prices[(prices >= min_price) & (prices <= max_price)]
    if filtered.empty:
        return "❌ Không tìm thấy sản phẩm phù hợp."
    order = filtered.sort_values().index
    
    all_idxs = list(order)
    unique_idxs = _get_unique_products(df_global, all_idxs, field, n)
    
    if not unique_idxs:
        return "❌ Không tìm thấy sản phẩm phù hợp."
    
    lines = []
    for idx in unique_idxs:
        r = df_global.loc[idx]
        currency = r.get('currency', 'USD')
        lines.append(f"- {r.get('name','')} ({r.get(field)} {currency})")
    
    return f"Gợi ý {len(unique_idxs)} sản phẩm trong khoảng {min_price} - {max_price} ({field}):\n" + "\n".join(lines)


@tool
def product_from_brand(brand_name: str, n: int = 3) -> str:
    """Get N products from a specific brand. 
    Use this when user asks about products from a brand (e.g., "Amazon Basic", "Sony", etc.).
    
    Args:
        brand_name: The brand name to search for (e.g., "Amazon", "Sony")
        n: Number of products to return (default 3, use -1 for all)
    
    Returns:
        List of products from that brand
    """
    global df_global
    
    try:
        mask = df_global["brandName"].str.contains(brand_name, case=False, na=False)
        df_brand = df_global[mask]
        
        if df_brand.empty:
            return f"❌ Không tìm thấy sản phẩm nào từ thương hiệu '{brand_name}'."
        
        df_brand_sorted = df_brand.sort_values(by="salePrice", ascending=False)
        
        if n == -1:
            n = len(df_brand_sorted)
        
        order = df_brand_sorted.index
        unique_idxs = _get_unique_products(df_global, list(order), "salePrice", n)
        
        if not unique_idxs:
            return f"❌ Không tìm thấy sản phẩm phù hợp sau khi loại bỏ trùng lặp. Tổng sản phẩm {brand_name}: {len(df_brand_sorted)}"
        
        lines = []
        for idx in unique_idxs:
            r = df_global.loc[idx]
            currency = r.get('currency', 'USD')
            price = r.get('salePrice', 'N/A')
            lines.append(f"- {r.get('name','')} ({price} {currency})")
        
        return f"Gợi ý {len(unique_idxs)} sản phẩm từ thương hiệu '{brand_name}':\n\n" + "\n".join(lines)
        
    except Exception as e:
        return f"❌ Lỗi khi tìm kiếm: {str(e)}"

@tool
def product_same_brand(product_name: str, n: int = 3) -> str:
    """Find N products from the same brand as the given product.
    Use this when user asks for products from the same brand as a specific product.
    Trigger keywords: "same brand", "cùng brand", "cùng thương hiệu", "tương tự", "giống brand".
    
    Args:
        product_name: The name of the product to find the brand from
        n: Number of products to return (default 3)
    
    Returns:
        List of N products from the same brand
    """
    global df_global
    
    try:
        mask = df_global["name"].str.contains(product_name, case=False, na=False)
        matching_products = df_global[mask]
        
        if matching_products.empty:
            return f"❌ Không tìm thấy sản phẩm '{product_name}' trong cơ sở dữ liệu."
        
        brand_name = matching_products.iloc[0]["brandName"]
        
        if pd.isna(brand_name) or brand_name == "":
            return f"❌ Sản phẩm '{product_name}' không có thông tin thương hiệu."
        
        brand_mask = df_global["brandName"].str.contains(brand_name, case=False, na=False)
        df_brand = df_global[brand_mask]
        
        original_product_name = matching_products.iloc[0]["name"]
        df_brand = df_brand[df_brand["name"] != original_product_name]
        
        if df_brand.empty:
            return f"❌ Không tìm thấy sản phẩm nào khác từ thương hiệu '{brand_name}'."
        
        df_brand_sorted = df_brand.sort_values(by="salePrice", ascending=False)
        order = df_brand_sorted.index
        
        unique_idxs = _get_unique_products(df_global, list(order), "salePrice", n)
        
        if not unique_idxs:
            return "❌ Không tìm thấy sản phẩm phù hợp sau khi loại bỏ trùng lặp."
        
        lines = []
        for idx in unique_idxs:
            r = df_global.loc[idx]
            currency = r.get('currency', 'USD')
            price = r.get('salePrice', 'N/A')
            lines.append(f"- {r.get('name','')} ({price} {currency})")
        
        return f"Gợi ý {len(unique_idxs)} sản phẩm khác từ thương hiệu '{brand_name}':\n" + "\n".join(lines)
    
    except Exception as e:
        return f"❌ Lỗi khi tìm kiếm: {str(e)}"

def chat():
    global df_global
    connect_milvus_lite()
    embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.1-8b-instant",  
        temperature=0,
    )
    retriever = Milvus(
        embedding_function=embedding,
        collection_name=COLLECTION_NAME,
        connection_args={"uri": MILVUS_URI},
    ).as_retriever(search_kwargs={"k": 3})

    csv_path = DATA_PATH
    if not os.path.exists(csv_path):
        csv_path = "amazon_data.csv"
    
    df_global = load_and_clean_data(str(csv_path))
    

    def search_text(q: str) -> str:
        """Search and retrieve relevant information from the knowledge base (Milvus vector database)
        and the local product dataset.
        
        Hybrid strategy:
        1️⃣ Direct DataFrame search when user asks about a specific product
        2️⃣ Vector (semantic) search via Milvus retriever as fallback
        
        Args:
            q: User query (Vietnamese or English)
        Returns:
            Answer string with sources or summary
        """
        try:
            # ================================
            # Chiến lược 1: Tìm trực tiếp trong DataFrame
            # ================================
            # Always try DataFrame search first for product queries
            if 'sản phẩm' in q.lower() or 'product' in q.lower():
                # Extract product name more carefully
                if 'sản phẩm' in q.lower():
                    product_name = q.split('sản phẩm')[-1].strip()
                else:
                    product_name = q.strip()
                
                # Clean up the product name
                product_name = product_name.replace('"', '').replace("'", "").strip()
                
                # Remove common query words to get cleaner product name
                query_words = ['của', 'brand', 'thương hiệu', 'mô tả', 'kích thước', 'giá', 'rating', 'đánh giá', 'đặc điểm', 'features']
                for word in query_words:
                    if word in product_name.lower():
                        # Split by the word and take the part that likely contains the product name
                        parts = product_name.lower().split(word)
                        if len(parts) > 1:
                            product_name = parts[1].strip()
                        else:
                            product_name = parts[0].strip()
                        break

                matching_products = None
                
                # Strategy 1: Exact substring match
                if product_name and len(product_name) > 3:
                    mask = df_global["name"].str.contains(product_name, case=False, na=False, regex=False)
                    matching_products = df_global[mask]
                    if not matching_products.empty:
                        print(f"🔍 Found {len(matching_products)} products with exact match: '{product_name}'")
                
                # Strategy 2: If no exact match, try with first few words
                if matching_products is None or matching_products.empty:
                    words = product_name.split()[:3]  # Take first 3 words
                    if words:
                        search_term = ' '.join(words)
                        mask = df_global["name"].str.contains(search_term, case=False, na=False, regex=False)
                        matching_products = df_global[mask]
                        if not matching_products.empty:
                            print(f"🔍 Found {len(matching_products)} products with partial match: '{search_term}'")
                
                # Strategy 3: If still no match, try with brand name (first word)
                if matching_products is None or matching_products.empty:
                    first_word = product_name.split()[0] if product_name.split() else ""
                    if first_word and len(first_word) > 2:
                        mask = df_global["name"].str.contains(first_word, case=False, na=False, regex=False)
                        matching_products = df_global[mask]
                        if not matching_products.empty:
                            print(f"🔍 Found {len(matching_products)} products with brand match: '{first_word}'")
                
                # If still no match, try to find similar products
                if matching_products is None or matching_products.empty:
                    print(f"⚠️ No direct match found for: '{product_name}'")
                    # Try to find any product that contains any word from the query
                    query_words = [word for word in product_name.split() if len(word) > 2]
                    for word in query_words:
                        mask = df_global["name"].str.contains(word, case=False, na=False, regex=False)
                        temp_matches = df_global[mask]
                        if not temp_matches.empty:
                            matching_products = temp_matches
                            print(f"🔍 Found {len(matching_products)} products with word match: '{word}'")
                            break

                if not matching_products.empty:
                    product = matching_products.iloc[0]
                    
                    # Check what specific field user is asking for
                    requested_field = None
                    field_keywords = {
                        'brand': 'brandName',
                        'thương hiệu': 'brandName', 
                        'mô tả': 'description',
                        'description': 'description',
                        'desc': 'description',
                        'giá': 'salePrice',
                        'price': 'salePrice',
                        'kích thước': 'size',
                        'size': 'size',
                        'chất liệu': 'material',
                        'material': 'material',
                        'đặc điểm': 'features',
                        'features': 'features',
                        'đánh giá': 'rating',
                        'rating': 'rating',
                        'danh mục': 'breadcrumbs',
                        'category': 'breadcrumbs',
                        'phong cách': 'style',
                        'style': 'style'
                    }
                    
                    for keyword, field in field_keywords.items():
                        if keyword in q.lower():
                            requested_field = field
                            break
                    
                    # If specific field requested, return only that field
                    # Find requested field
                    if requested_field and requested_field in product and pd.notna(product[requested_field]):
                        field_labels = {
                            "material": "Chất liệu",
                            "features": "Đặc điểm", 
                            "description": "Mô tả",
                            "salePrice": "Giá bán",
                            "currency": "Loại tiền",
                            "rating": "Đánh giá",
                            "brandName": "Thương hiệu",
                            "breadcrumbs": "Danh mục",
                            "style": "Phong cách",
                            "size": "Kích thước",
                        }
                        
                        label = field_labels.get(requested_field, requested_field)
                        value = str(product[requested_field])
                        
                        value = value.replace('\\', '')  # Remove backslashes
                        value = value.replace('{', '').replace('}', '')  # Remove braces
                        value = value.replace('"', '')  # Remove quotes
                        value = value.replace('[', '').replace(']', '')  # Remove brackets
                        value = value.replace('\\"', '"')  # Fix escaped quotes
                        
                        import re
                        value = re.sub(r'\s+', ' ', value).strip()
                        
                        if requested_field == 'description':
                            if len(value) > 800:
                                value = value[:800] + "..."
                            return f"{label} của sản phẩm '{product.get('name', 'N/A')}':\n\n{value}"
                        else:
                            if len(value) > 500:
                                value = value[:500] + "..."
                            return f"{label} của sản phẩm '{product.get('name', 'N/A')}': {value}"

                    result = f"🔍 Thông tin sản phẩm: {product.get('name', 'N/A')}\n"

                    
                    field_map = {
                        "material": "Chất liệu",
                        "features": "Đặc điểm",
                        "description": "Mô tả",
                        "salePrice": "Giá bán",
                        "currency": "Loại tiền",
                        "rating": "Đánh giá",
                        "brandName": "Thương hiệu",
                        "breadcrumbs": "Danh mục",
                        "style": "Phong cách",
                        "size": "Kích thước",
                    }

                    for col, label in field_map.items():
                        if col in product and pd.notna(product[col]):
                            value = str(product[col])
                            
                            
                            if col == 'breadcrumbs':
                                value = value.replace('\\', '')  # Remove backslashes
                                value = value.replace('{', '').replace('}', '')  # Remove braces
                                value = value.replace('"', '')  # Remove quotes
                                value = value.replace('[', '').replace(']', '')  # Remove brackets
                                value = value.replace('\\"', '"')  # Fix escaped quotes
                                
                                
                                import re
                                value = re.sub(r'name:\s*', '', value)  # Remove "name:" 
                                value = re.sub(r'\s*,\s*name:\s*', ' > ', value)  # Replace ", name:" with " > "
                                value = re.sub(r'\s+', ' ', value).strip()  # Clean up spaces
                                
                                if len(value) > 200:
                                    value = value[:200] + "..."
                                result += f"{label}: {value}\n"
                            else:
                                value = value.replace('\\', '')  # Remove backslashes
                                value = value.replace('{', '').replace('}', '')  # Remove braces
                                value = value.replace('"', '')  # Remove quotes
                                value = value.replace('[', '').replace(']', '')  # Remove brackets
                                value = value.replace('\\"', '"')  # Fix escaped quotes
                                
                                import re
                                value = re.sub(r'\s+', ' ', value).strip()
                                
                                if len(value) > 300:
                                    value = value[:300] + "..."
                                result += f"{label}: {value}\n"

                    return result

            # ================================
            # 2️⃣ Chiến lược 2: Vector search qua retriever
            # ================================
            docs = retriever.invoke(q)
            if not docs:
                return "Không tìm thấy thông tin phù hợp trong cơ sở dữ liệu."

            seen_sources = set()
            unique_docs = []

            for doc in docs[:10]:
                source = doc.metadata.get("id") or doc.metadata.get("url") or doc.metadata.get("name", "unknown")
                if source in seen_sources:
                    continue
                seen_sources.add(source)

                import re
                clean_text = re.sub(r"<[^>]+>", " ", doc.page_content)
                clean_text = re.sub(r"\s+", " ", clean_text).strip()
                unique_docs.append((source, clean_text[:800]))

                if len(unique_docs) >= 5:
                    break

            if not unique_docs:
                return "Không tìm thấy thông tin phù hợp."

            context = "\n\n".join(f"[Tài liệu {i+1}]\n{text}" for i, (_, text) in enumerate(unique_docs))

            # Prompt cho LLM - improved to be more helpful
            prompt = f"""Dựa trên ngữ cảnh sau, hãy trả lời câu hỏi một cách ngắn gọn, chính xác.

Câu hỏi: {q}

Ngữ cảnh:
{context}

Hướng dẫn:
- Nếu có thông tin phù hợp trong ngữ cảnh, hãy trả lời trực tiếp
- Nếu không đủ thông tin, hãy nói: "Không đủ thông tin để trả lời câu hỏi này."
- Trả lời bằng tiếng Việt, ngắn gọn và hữu ích
- Nếu có thể, hãy cung cấp thông tin liên quan có sẵn"""

            resp = llm.invoke(prompt)
            answer = resp.content if hasattr(resp, "content") else str(resp)

            sources_list = "\n".join(f"📄 Nguồn {i+1}: {src}" for i, (src, _) in enumerate(unique_docs))
            return f"{answer}\n\n{sources_list}"

        except Exception as e:
            return f"❌ Lỗi khi tìm kiếm: {str(e)}"


    tools = [
        get_highest_price,
        get_lowest_price,
        suggest_by_price,
        recommend_product_by_range,
        search_text,
        product_from_brand,
        product_same_brand,
    ]

    system_prompt = """You are a helpful Vietnamese e-commerce assistant. 

CRITICAL RULES:
1. Call EXACTLY ONE tool per user question
2. Pass the FULL ORIGINAL QUERY to the tool (do not extract or modify the query)
3. After receiving tool results, IMMEDIATELY provide a final answer to the user
4. DO NOT call multiple tools for the same question
5. DO NOT call the same tool multiple times
6. Be concise and helpful in Vietnamese

TOOL SELECTION - CHOOSE ONLY ONE:

For product information questions:
- "thông tin về sản phẩm X" → search_text
- "mô tả của sản phẩm X" → search_text
- "kích thước của sản phẩm X" → search_text
- "brand của sản phẩm X" → search_text
- "thương hiệu của sản phẩm X" → search_text

For price comparison:
- "sản phẩm đắt nhất" → get_highest_price
- "sản phẩm rẻ nhất" → get_lowest_price
- "brand của sản phẩm đắt nhất" → get_highest_price
- "brand của sản phẩm rẻ nhất" → get_lowest_price

For recommendations:
- "gợi ý sản phẩm gần giá X" → suggest_by_price
- "sản phẩm từ X đến Y" → recommend_product_by_range
- "sản phẩm từ thương hiệu X" → product_from_brand
- "gợi ý sản phẩm cùng brand với X" → product_same_brand

EXAMPLES:
Q: "brand của sản phẩm Mendini by Cecilio B Flat Baritone Horn" → search_text("brand của sản phẩm Mendini by Cecilio B Flat Baritone Horn")
Q: "brand của sản phẩm đắt nhất" → get_highest_price("brand của sản phẩm đắt nhất")
Q: "mô tả của sản phẩm Sony WH-1000XM4" → search_text("mô tả của sản phẩm Sony WH-1000XM4")
Q: "gợi ý 3 sản phẩm từ brand amazon basics" → product_from_brand("gợi ý 3 sản phẩm từ brand amazon basics")

IMPORTANT: Always pass the COMPLETE user query to the tool, never extract just the product name!

IMPORTANT: Call only ONE tool, then provide the final answer immediately."""
    
    agent_executor = create_react_agent(llm, tools, prompt=system_prompt)

    print("🤖 Chatbot TMĐT (gõ 'exit' để thoát)\n")
    while True:
        q = input("\nBạn: ")
        if q.strip().lower() in {"exit", "quit"}:
            break

        q_stripped = q.strip().lower()
        greetings = {"xin chào", "chào", "hello", "hi", "hey", "chao", "alo"}
        if q_stripped in greetings or any(q_stripped.startswith(g + " ") for g in greetings):
            print("\nBot:", "Xin chào! Tôi có thể giúp gì cho bạn?")
            continue
        try:
            final_answer = None
            tools_used = []
            tool_called = False
            tool_result = None
            
            config = {"recursion_limit": 15}  # Max 15 steps
            for chunk in agent_executor.stream({"messages": [HumanMessage(content=q)]}, config=config):
                if "agent" in chunk and "messages" in chunk["agent"]:
                    for msg in chunk["agent"]["messages"]:
                        if hasattr(msg, "content") and msg.content:
                            if msg.content.startswith("<function="):
                                tool_name = msg.content.split("=")[1].split("{")[0] if "{" in msg.content else msg.content.split("=")[1].rstrip(">")
                                if tool_name not in tools_used:
                                    tools_used.append(tool_name)
                                    tool_called = True
                                    print(f"🔧 [Tool] Đang gọi: {tool_name}")
                            else:
                                if not tool_called:
                                    print(f"🤖 Agent response: {msg.content}")
                                    final_answer = msg.content
                                else:
                                    print(f"🚫 Ignoring agent response after tool: {msg.content}")
                
                elif "tools" in chunk and "messages" in chunk["tools"]:
                    for msg in chunk["tools"]["messages"]:
                        if hasattr(msg, "name"):
                            print(f"✅ [Tool] Hoàn thành: {msg.name}")
                            if hasattr(msg, "content") and msg.content:
                                print(f"🔍 Tool result: {msg.content}")
                                tool_result = msg.content
            if tool_result:
                print(f"\nBot: {tool_result}\n")
            elif final_answer:
                print(f"\nBot: {final_answer}\n")
            else:
                print("\nBot: Không có câu trả lời.\n")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            import traceback
            traceback.print_exc()