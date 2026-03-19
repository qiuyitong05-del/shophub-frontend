import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from shop_app.models import ShopUser, Address

def check_addresses():
    users = ShopUser.objects.all()
    for u in users:
        addrs = Address.objects.filter(user=u)
        print(f"User {u.username} (ID: {u.id}): {addrs.count()} addresses")
        for a in addrs:
            full = f"{a.province} {a.city} {a.detail_address}".strip()
            print(f"  - {full} (Default? Maybe first one is used)")

if __name__ == '__main__':
    check_addresses()
