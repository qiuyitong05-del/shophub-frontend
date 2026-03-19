
import os
import sys
import django
from datetime import timedelta
from django.utils import timezone
import random

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from shop_app.models import ShopUser, Order, OrderItem, Product, Address

def create_test_orders():
    # Ensure user exists
    user, created = ShopUser.objects.get_or_create(username='testuser', defaults={'email': 'test@example.com'})
    if created:
        user.set_password('testpass123')
        user.save()
        Address.objects.create(user=user, province='Test Province', city='Test City', detail_address='Test Address')
        print(f"Created user 'testuser'")
    else:
        print(f"Using user 'testuser'")

    # Ensure product exists
    product = Product.objects.first()
    if not product:
        print("No products found. Please run populate_furniture.py first.")
        return

    # Stages to generate orders for
    # We want orders OLDER than these days
    stages = [30, 60, 120, 360]
    
    for days in stages:
        # Create a few orders for each stage
        for i in range(2): 
            # Set created_at to days + small buffer ago
            created_at = timezone.now() - timedelta(days=days + 2)
            
            order = Order.objects.create(
                user=user,
                status='Shipped',
                total_amount=product.price,
                shipping_address='Test Address',
                created_at=created_at, # This might be overridden by auto_now_add=True
                shipped_at=created_at + timedelta(days=1)
            )
            
            # Hack to update created_at because auto_now_add prevents setting it on create
            Order.objects.filter(id=order.id).update(created_at=created_at)
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=1,
                unit_price=product.price
            )
            print(f"Created order {order.id} for {days}+ days ago")

if __name__ == '__main__':
    create_test_orders()
