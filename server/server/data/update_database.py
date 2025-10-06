import os
import sys
import django
import json

# Add the Django project to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from shop.models import Product

def update_database():
    """Update database with products from processed_products.json"""
    
    json_file = 'processed_products.json'
    
    # Check if JSON file exists
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found")
        return
    
    try:
        # Load JSON data
        with open(json_file, 'r', encoding='utf-8') as f:
            products_data = json.load(f)
        
        print(f"Loaded {len(products_data)} products from JSON")
        
        # Delete existing products
        existing_count = Product.objects.count()
        if existing_count > 0:
            print(f"Deleting {existing_count} existing products...")
            Product.objects.all().delete()
        
        # Create new products
        print("Creating new products...")
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
        
        print(f"Successfully created {created_count} products")
        
        # Verify
        final_count = Product.objects.count()
        print(f"Total products in database: {final_count}")
        
        # Show sample
        if final_count > 0:
            sample_product = Product.objects.first()
            print(f"\nSample product in database:")
            print(f"ID: {sample_product.id}")
            print(f"Name: {sample_product.name}")
            print(f"Price: {sample_product.price}")
            print(f"Discount: {sample_product.discount}")
            print(f"Labels: {sample_product.get_labels_list()}")
        
    except Exception as e:
        print(f"Error updating database: {e}")

if __name__ == "__main__":
    update_database()
