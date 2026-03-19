import os
import django
import sys
from decimal import Decimal

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from shop_app.models import Order, OrderItem

def fix_order_totals():
    orders = Order.objects.all()
    count = 0
    for order in orders:
        # Calculate expected total from items
        items = OrderItem.objects.filter(order=order)
        item_total = Decimal('0.00')
        for item in items:
            item_total += item.unit_price * item.quantity
            
        # Check if shipping fee is needed
        if item_total < 999:
            expected_total_with_shipping = item_total + Decimal('20.00')
            
            # Check if current total matches item_total (meaning shipping was missing)
            # We use a small epsilon for float comparison safety, though Decimal should be exact
            if abs(order.total_amount - item_total) < Decimal('0.01'):
                print(f"Order {order.id}: Total {order.total_amount} matches item total {item_total}. Adding shipping fee.")
                order.total_amount = expected_total_with_shipping
                order.save()
                count += 1
            elif abs(order.total_amount - expected_total_with_shipping) < Decimal('0.01'):
                print(f"Order {order.id}: Total {order.total_amount} already includes shipping.")
            else:
                print(f"Order {order.id}: Total {order.total_amount} mismatch (Items: {item_total}). Skipping.")
        else:
            # Over 999, no shipping fee needed
            if abs(order.total_amount - item_total) > Decimal('0.01'):
                 # Maybe check if we need to fix it? User said "if > 999 it's fine"
                 # But if it's mismatching, maybe we should fix it to be sum of items?
                 # Let's just leave it if > 999 as requested ("if > 999 it's fine")
                 pass

    print(f"Fixed {count} orders.")

if __name__ == '__main__':
    fix_order_totals()
