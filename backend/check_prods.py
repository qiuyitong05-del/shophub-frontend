import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from shop_app.models import Category, Product

for cat_id in [17, 18, 19, 21, 30]:
    cat = Category.objects.get(id=cat_id)
    print(f"\nCategory: {cat.name}")
    for p in cat.product_set.all():
        print(f" - {p.name}")
