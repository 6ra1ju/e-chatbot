import csv
import json
import os
import sys
import django
import pandas as pd

# Ensure project is on path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from shop.models import Product


def to_int(value, default: int = 0) -> int:
    """Convert value to integer with fallback"""
    try:
        if value is None or str(value).strip() == "":
            return default
        # Handle currency formatting like $44.99
        cleaned = str(value).replace('$', '').replace(',', '').strip()
        return int(float(cleaned))
    except Exception:
        return default


def to_float(value, default: float = None) -> float:
    """Convert value to float with fallback"""
    try:
        if value is None or str(value).strip() == "":
            return default
        cleaned = str(value).replace('$', '').replace(',', '').strip()
        return float(cleaned)
    except Exception:
        return default


def extract_first_image(image_field: str) -> str:
    """Extract first image URL from JSON-like field"""
    if not image_field or not isinstance(image_field, str):
        return ""
    
    try:
        # Try to parse as JSON first
        parsed = json.loads(image_field)
        if isinstance(parsed, list) and len(parsed) > 0:
            return str(parsed[0])
    except Exception:
        pass
    
    # Fallback: try to extract from comma-separated values
    cleaned = image_field.strip().strip('[]')
    
    # Use regex to find quoted URLs
    import re
    urls = re.findall(r'"([^"]*)"', cleaned)
    
    # Filter for actual Amazon image URLs
    amazon_urls = [url for url in urls if 'amazon.com/images' in url and url.endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    
    if amazon_urls:
        return amazon_urls[0]
    
    # Final fallback: split by comma
    parts = [p.strip().strip('"') for p in cleaned.split(',') if p.strip()]
    if parts:
        return parts[0]
    
    return ""

def load_and_clean_data(csv_path: str) -> pd.DataFrame:
    """Load and clean Amazon data"""
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.replace(r"[^0-9a-zA-Z_]", "_", regex=True)
    required_cols = [
        "additionalProperties","brandName","breadcrumbs","color","currency","current_depth","description",
        "descriptionRaw","features","imageUrls","inStock","listedPrice","material","name","new_path","nodeName",
        "rating","reviewCount","salePrice","size","style","variants","weight_rawUnit","weight_unit","weight_value"
    ]
    df_clean = df.dropna(subset=[c for c in required_cols if c in df.columns])
    df_clean = df_clean[["additionalProperties","brandName","breadcrumbs", "description", "descriptionRaw",
        "features", "salePrice","listedPrice", "material", "name", "rating", "size", "style", "imageUrls"]
    ]
    return df_clean

def process_amazon_csv(
    input_csv_path: str = os.path.join(os.path.dirname(__file__), "..", "..", "..", "chatbot", "amazon_data.csv"),
    output_json_path: str = os.path.join(os.path.dirname(__file__), "processed_amazon_products.json"),
) -> None:
    """Process Amazon CSV and create processed_amazon_products.json"""
    
    products = []
    processed_count = 0
    
    print(f"Reading Amazon data from: {input_csv_path}")
    
    df_clean = load_and_clean_data(input_csv_path)
    
    for idx, row in df_clean.iterrows():
        name = (row.get("name") or "").strip()
        if not name:
            continue
            
        try:
                
            # Price handling
            sale_price = to_float(row.get("salePrice"))
            listed_price = to_float(row.get("listedPrice"))
            
            final_price_vnd = int(sale_price * 24000)
            original_price_vnd = int(listed_price * 24000)
            
            # Calculate discount
            discount = round((1 - (final_price_vnd / original_price_vnd)) * 100)
            
            # Rating and reviews
            rating = to_float(row.get("rating"))
            review_count = to_int(row.get("reviewCount"), 0)
            
            # Image
            image_url = extract_first_image(row.get("imageUrls", ""))
            
            # Brand and category info
            brand = (row.get("brandName") or "").strip()
            category = (row.get("nodeName") or "").strip()
            
            # Create labels
            labels = []
            if brand:
                labels.append(brand)
            if category:
                labels.append(category)
            labels.extend(["amazon", "imported"])
            
            product = {
                "name": name,
                "price": final_price_vnd,
                "original_price": original_price_vnd,
                "discount": discount,
                "rating": rating,
                "sold_count": review_count,  # Using review count as proxy for sold count
                "image": image_url,
                "labels": labels,
            }
            
            products.append(product)
            processed_count += 1
        except Exception as e:
            print(f"Error processing product {name}: {e}")
            continue
            
            if processed_count % 100 == 0:
                print(f"Processed {processed_count} products...")
    
    # Save to JSON
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully processed {len(products)} Amazon products")
    print(f"Output saved to: {output_json_path}")
    
    # Show sample
    if products:
        print("\nSample Amazon product:")
        print(json.dumps(products[0], ensure_ascii=False, indent=2))


def update_database_with_amazon():
    """Update database with Amazon products"""
    
    json_file = 'processed_amazon_products.json'
    
    # Check if JSON file exists
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found. Please run process_amazon_csv first.")
        return
    
    try:
        # Load JSON data
        with open(json_file, 'r', encoding='utf-8') as f:
            products_data = json.load(f)
        
        print(f"Loaded {len(products_data)} Amazon products from JSON")
        
        # Delete existing products
        existing_count = Product.objects.count()
        if existing_count > 0:
            print(f"Deleting {existing_count} existing products...")
            Product.objects.all().delete()
        
        # Create new Amazon products
        print("Creating new Amazon products...")
        created_count = 0
        
        for product_data in products_data:
            try:
                product = Product.objects.create(
                    name=product_data['name'],
                    price=product_data['price'],
                    original_price=product_data.get('original_price'),
                    discount=product_data.get('discount'),
                    rating=product_data.get('rating'),
                    sold_count=product_data.get('sold_count'),
                    image=product_data.get('image')
                )
                
                # Set labels if provided
                if 'labels' in product_data:
                    product.set_labels_list(product_data['labels'])
                    product.save()
                
                created_count += 1
                
                if created_count % 100 == 0:
                    print(f"Created {created_count} products...")
                    
            except Exception as e:
                print(f"Error creating product {product_data.get('name', 'Unknown')}: {e}")
                continue
        
        print(f"Successfully created {created_count} Amazon products")
        
        # Verify
        final_count = Product.objects.count()
        print(f"Total products in database: {final_count}")
        
        # Show sample
        if final_count > 0:
            sample_product = Product.objects.first()
            print(f"\nSample Amazon product in database:")
            print(f"ID: {sample_product.id}")
            print(f"Name: {sample_product.name}")
            print(f"Price: {sample_product.price}")
            print(f"Discount: {sample_product.discount}")
            print(f"Labels: {sample_product.get_labels_list()}")
        
    except Exception as e:
        print(f"Error updating database: {e}")


if __name__ == "__main__":
    print("Processing Amazon data...")
    process_amazon_csv()
    
    print("\nUpdating database...")
    update_database_with_amazon()
