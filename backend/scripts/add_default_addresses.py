import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from shop_app.models import ShopUser, Address

def add_default_addresses():
    users = ShopUser.objects.all()
    count = 0
    for u in users:
        # Check if user has any address
        if not Address.objects.filter(user=u).exists():
            # Create a default address
            # Using a generic placeholder or deriving from username if needed, 
            # but usually "Default Address" is fine for testing/migration.
            # User requirement: "Please give *every* user a default address".
            # Let's make it look slightly realistic.
            Address.objects.create(
                user=u,
                province='Guangdong',
                city='Guangzhou',
                detail_address=f'Default Street {u.id}, Apt {u.id}'
            )
            print(f"Added address for user {u.username} (ID: {u.id})")
            count += 1
        else:
            print(f"User {u.username} already has address.")
            
    print(f"Added {count} addresses.")

if __name__ == '__main__':
    add_default_addresses()
