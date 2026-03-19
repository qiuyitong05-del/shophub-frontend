
import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from shop_app.models import Product, Tag, ProductTag

def add_tags():
    print("Starting tag initialization...")
    tags = ['Modern', 'Vintage', 'Eco-friendly', 'Sale', 'New Arrival', 'Best Seller', 'Handmade', 'Premium']
    
    existing_tags = []
    for t_name in tags:
        tag, created = Tag.objects.get_or_create(name=t_name)
        existing_tags.append(tag)
        if created:
            print(f"Created tag: {t_name}")
    
    print(f"Total tags available: {len(existing_tags)}")
    
    products = Product.objects.all()
    print(f"Found {products.count()} products.")
    
    # Clear existing tags to avoid duplicates or mess
    ProductTag.objects.all().delete()
    print("Cleared existing product tags.")
    
    count = 0
    for p in products:
        # Add 1-3 random tags
        num_tags = random.randint(1, 3)
        selected_tags = random.sample(existing_tags, num_tags)
        for tag in selected_tags:
            ProductTag.objects.create(product=p, tag=tag)
            count += 1
            
    print(f"Successfully added {count} tags across {products.count()} products.")

if __name__ == '__main__':
    add_tags()
