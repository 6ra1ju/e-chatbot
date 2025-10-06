import os
import sys
import django

# Add the Django project to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from shop.models import Product

def update_discounts():
    """Update discount for all products with fine-grained distribution (10-30% with step 1)"""
    
    # Get all products
    products = Product.objects.all()
    total_products = products.count()
    
    if total_products == 0:
        print("No products found in database")
        return
    
    print(f"Updating discounts for {total_products} products...")
    
    # Discount range: 10-30 with step 1
    discount_range = list(range(10, 31))  # [10, 11, 12, ..., 30]
    num_discounts = len(discount_range)
    
    # Statistics
    discount_stats = {discount: 0 for discount in discount_range}
    
    # Update each product
    for i, product in enumerate(products):
        # Assign discount based on product ID for consistency
        discount = discount_range[product.id % num_discounts]
        
        # Update product
        product.discount = discount
        product.save()
        
        # Update statistics
        discount_stats[discount] += 1
        
        # Progress indicator
        if (i + 1) % 100 == 0:
            print(f"Updated {i + 1}/{total_products} products...")
    
    print(f"Successfully updated {total_products} products")
    
    # Show statistics
    print("\nDiscount distribution:")
    for discount in sorted(discount_stats.keys()):
        count = discount_stats[discount]
        percentage = (count / total_products) * 100
        print(f"{discount}%: {count} products ({percentage:.1f}%)")
    
    # Show sample products
    print("\nSample products:")
    sample_products = Product.objects.all()[:5]
    for product in sample_products:
        print(f"Product #{product.id}: {product.name} - {product.discount}% discount")

if __name__ == "__main__":
    update_discounts()
