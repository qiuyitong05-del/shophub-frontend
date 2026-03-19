import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from shop_app.models import Product

def check_products():
    print("Checking products for null category...")
    bad_products = Product.objects.filter(category__isnull=True)
    if bad_products.exists():
        print(f"Found {bad_products.count()} products with null category!")
        for p in bad_products:
            print(f"Product {p.id}: {p.name}")
    else:
        print("All products have valid categories.")

if __name__ == '__main__':
    check_products()
