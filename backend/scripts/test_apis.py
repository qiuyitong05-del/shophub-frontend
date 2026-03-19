import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from rest_framework.test import APIRequestFactory

from shop_app.views import product_detail, get_cart, orders_list, product_reviews
from shop_app.models import Product, ShopUser

def test_apis():
    factory = APIRequestFactory()
    
    print("Testing Product Detail API...")
    p = Product.objects.first()
    if p:
        req = factory.get(f'/api/products/{p.id}/')
        try:
            resp = product_detail(req, pk=p.id)
            print(f"Product Detail Status: {resp.status_code}")
        except Exception as e:
            print(f"Product Detail Failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("No products to test.")

    print("\nTesting Reviews API...")
    if p:
        req = factory.get(f'/api/products/{p.id}/reviews/')
        try:
            resp = product_reviews(req, product_id=p.id)
            print(f"Reviews Status: {resp.status_code}")
        except Exception as e:
            print(f"Reviews Failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_apis()
