import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from shop_app.models import ShopUser

username = 'admin'
password = 'admin123456'
email = 'admin@example.com'

if not ShopUser.objects.filter(username=username).exists():
    print(f"Creating superuser {username}...")
    user = ShopUser.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser created successfully.")
else:
    print(f"Superuser {username} already exists.")
    user = ShopUser.objects.get(username=username)
    if not user.is_staff or not user.is_superuser:
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print("Updated existing user to admin status.")
