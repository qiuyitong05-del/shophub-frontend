import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from shop_app.models import Category, Product

def move_product(prod_name, new_cat_id):
    try:
        p = Product.objects.get(name=prod_name)
        p.category_id = new_cat_id
        p.save()
    except Product.DoesNotExist:
        pass
    except Product.MultipleObjectsReturned:
        pass

# Move specific products
move_product("Solid Ash Dining Table", 23) # Dining Room
move_product("Compact Home Office Desk", 24) # Office
move_product("Ergonomic Mesh Office Chair", 24) # Office

# Move categories
storage_cat = Category.objects.get(id=28) # Storage & Organization
for p in Category.objects.get(id=17).product_set.all():
    p.category = storage_cat
    p.save()

decor_cat = Category.objects.get(id=26)
decor_cat.name = "Home Decor"
decor_cat.save()

for p in Category.objects.get(id=21).product_set.all():
    p.category = decor_cat
    p.save()

living_cat = Category.objects.get(id=15)
for p in Category.objects.get(id=30).product_set.all(): # TestCat
    p.category = living_cat
    p.save()

# Delete redundant categories
Category.objects.filter(id__in=[17, 18, 19, 21, 22, 30]).delete()

print("Cleanup complete!")
for c in Category.objects.all():
    print(f"ID: {c.id}, Name: '{c.name}', Products count: {c.product_set.count()}")
