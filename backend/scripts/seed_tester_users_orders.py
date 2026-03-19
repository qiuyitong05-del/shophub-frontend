import os
import sys
import django
from datetime import timedelta
from django.utils import timezone
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from shop_app.models import ShopUser, Order, OrderItem, Product, Address


def ensure_user(username: str, password: str):
    user, created = ShopUser.objects.get_or_create(
        username=username,
        defaults={'email': f'{username}@example.com'}
    )
    user.set_password(password)
    user.save()

    Address.objects.get_or_create(
        user=user,
        defaults={
            'province': 'Test Province',
            'city': 'Test City',
            'detail_address': 'Test Address'
        }
    )
    return user, created


def seed_orders_for_user(user: ShopUser, stages_days, orders_per_stage: int = 2):
    Order.objects.filter(user=user).delete()

    products = list(Product.objects.filter(is_active=True))
    if not products:
        products = list(Product.objects.all())
    if not products:
        raise RuntimeError("No products found. Please run populate_furniture.py first.")

    for days in stages_days:
        for _ in range(orders_per_stage):
            product = random.choice(products)
            quantity = 1
            created_at = timezone.now() - timedelta(days=days)
            shipped_at = created_at + timedelta(days=1)

            order = Order.objects.create(
                user=user,
                status='Shipped',
                total_amount=product.price * quantity,
                shipping_address='Test Address',
                shipped_at=shipped_at
            )
            Order.objects.filter(id=order.id).update(created_at=created_at)

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.price
            )


def run():
    stages = [30, 60, 120, 360]
    for username in ['tester1', 'tester2']:
        user, created = ensure_user(username, 'test123')
        seed_orders_for_user(user, stages, orders_per_stage=2)
        print(f"Seeded orders for {username} (created: {created})")


if __name__ == '__main__':
    run()
