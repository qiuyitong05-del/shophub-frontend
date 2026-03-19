import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from shop_app.models import Coupon

coupons = Coupon.objects.filter(code='HELPFUL_REVIEW_5')
print(f"Found {coupons.count()} coupons with code HELPFUL_REVIEW_5")

if coupons.count() > 1:
    print("Deleting duplicates...")
    for c in coupons[1:]:
        c.delete()
    print("Duplicates deleted.")
