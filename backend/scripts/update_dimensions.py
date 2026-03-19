import os
import django
import random
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from shop_app.models import Product, ProductTag, Tag

def update_products():
    print("Updating products with dimensions...")
    products = Product.objects.all()
    count = 0
    
    # Ensure Customizable tag exists
    custom_tag, _ = Tag.objects.get_or_create(name='Customizable')
    
    for p in products:
        updated = False
        
        # Add random dimensions if missing
        if not p.width:
            p.width = random.randint(50, 200)
            updated = True
        if not p.height:
            p.height = random.randint(50, 250)
            updated = True
        if not p.depth:
            p.depth = random.randint(30, 100)
            updated = True
            
        # Check if it should be customizable
        # Keywords: Table, Cabinet, Sofa, Bed, Chair, Shelf
        name_lower = p.name.lower()
        if any(k in name_lower for k in ['table', 'cabinet', 'sofa', 'bed', 'shelf', 'wardrobe', 'desk']):
            if not p.is_customizable:
                p.is_customizable = True
                updated = True
            
            # Add tag
            if not ProductTag.objects.filter(product=p, tag=custom_tag).exists():
                ProductTag.objects.create(product=p, tag=custom_tag)
                print(f"Added 'Customizable' tag to {p.name}")
        
        if updated:
            p.save()
            count += 1
            print(f"Updated {p.name}: {p.width}x{p.height}x{p.depth}, Customizable: {p.is_customizable}")

    print(f"Finished updating {count} products.")

if __name__ == '__main__':
    update_products()
