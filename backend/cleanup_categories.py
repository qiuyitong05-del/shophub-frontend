import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from shop_app.models import Category, Product

# 1. Inspect existing categories
categories = Category.objects.all()
print("Current Categories:")
for c in categories:
    print(f"ID: {c.id}, Name: '{c.name}', Products count: {c.product_set.count()}")

