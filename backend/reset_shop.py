
import os
import django
import random
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from shop_app.models import Product, Category, Tag, ProductTag, Order, OrderItem, CartItem, Review, BrowseHistory, WishlistItem, ProductPhoto

def reset_and_populate():
    print("WARNING: This will delete all shop data (Orders, Products, etc).")
    
    # 1. Clean up dependent data first (though CASCADE handles most, being explicit helps logic)
    print("Deleting Orders and OrderItems...")
    Order.objects.all().delete() # Cascades to OrderItem
    
    print("Deleting CartItems...")
    CartItem.objects.all().delete()
    
    print("Deleting Reviews...")
    Review.objects.all().delete()
    
    print("Deleting History and Wishlists...")
    BrowseHistory.objects.all().delete()
    WishlistItem.objects.all().delete()
    
    print("Deleting Products, Categories, Tags...")
    Product.objects.all().delete() # Cascades to ProductTag, ProductPhoto
    Category.objects.all().delete()
    Tag.objects.all().delete()

    print("Data cleared. Starting population...")

    # 2. Create Categories
    categories_data = [
        'Living Room Furniture',
        'Bedroom Furniture',
        'Storage & Shelving',
        'Tables & Desks',
        'Office Chairs',
        'Lighting',
        'Home Decor',
        'Kitchen & Dining'
    ]
    
    category_map = {}
    for cat_name in categories_data:
        cat = Category.objects.create(name=cat_name)
        category_map[cat_name] = cat
        print(f"Created Category: {cat_name}")

    # 3. Create Tags
    tags_data = [
        'Best Seller', 'New Arrival', 'Sale', 'Eco-friendly', 
        'Modern Style', 'Vintage Style', 'Minimalist', 'Industrial',
        'Handmade', 'Solid Wood', 'Luxury', 'Budget Friendly'
    ]
    
    tag_map = {}
    for t_name in tags_data:
        tag = Tag.objects.create(name=t_name)
        tag_map[t_name] = tag
        print(f"Created Tag: {t_name}")

    # 4. Create Products with Descriptive Names
    products_data = [
        {
            'name': 'Classic High-Back Wing Chair',
            'category': 'Living Room Furniture',
            'price': 249.99,
            'description': 'A timeless classic that brings elegance and comfort to your living room. The high back provides excellent neck support, making it perfect for reading or relaxing.',
            'features': '<ul><li>Durable fabric upholstery</li><li>Solid wood legs</li><li>Ergonomic high back design</li><li>Available in multiple colors</li></ul>',
            'tags': ['Vintage Style', 'Best Seller', 'Luxury']
        },
        {
            'name': 'Modern 3-Seater Memory Foam Sofa',
            'category': 'Living Room Furniture',
            'price': 599.00,
            'description': 'Experience ultimate comfort with this spacious 3-seater sofa. Featuring memory foam cushions that adapt to your body shape and wide armrests for added relaxation.',
            'features': '<ul><li>High-density memory foam</li><li>Removable and washable covers</li><li>Sturdy solid wood frame</li><li>Soft-touch fabric</li></ul>',
            'tags': ['Modern Style', 'New Arrival', 'Family Friendly']
        },
        {
            'name': 'Minimalist Oak Veneer Bed Frame',
            'category': 'Bedroom Furniture',
            'price': 229.50,
            'description': 'A clean, simple design that fits perfectly in any modern bedroom. Made with real oak veneer, this bed frame is sturdy, stylish, and easy to assemble.',
            'features': '<ul><li>Real oak wood veneer</li><li>Adjustable bed sides for different mattress heights</li><li>Compatible with under-bed storage boxes</li></ul>',
            'tags': ['Minimalist', 'Best Seller', 'Eco-friendly']
        },
        {
            'name': 'Standard 5-Tier Bookcase White',
            'category': 'Storage & Shelving',
            'price': 69.99,
            'description': 'The world’s most popular bookcase. Adjustable shelves allow you to customize the storage space according to your needs. Perfect for books, display items, and storage boxes.',
            'features': '<ul><li>5 adjustable shelves</li><li>Stable construction</li><li>Easy to clean surface</li><li>Wall anchor included for safety</li></ul>',
            'tags': ['Budget Friendly', 'Best Seller', 'Modern Style']
        },
        {
            'name': 'Versatile 4x4 Cube Storage Unit',
            'category': 'Storage & Shelving',
            'price': 119.00,
            'description': 'A flexible storage solution that can be placed vertically or horizontally. Use it as a room divider, a bookshelf, or a display unit. Compatible with various drawer inserts and boxes.',
            'features': '<ul><li>16 storage cubes</li><li>Finished on all sides</li><li>Can be used as a room divider</li><li>Scratch-resistant finish</li></ul>',
            'tags': ['Modern Style', 'Minimalist', 'Storage Solution']
        },
        {
            'name': 'Solid Ash Dining Table',
            'category': 'Tables & Desks',
            'price': 149.00,
            'description': 'A beautiful dining table with a handcrafted look. The visible wood grain gives each table a unique character. Easy to assemble and highly durable.',
            'features': '<ul><li>Solid ash wood legs</li><li>Ash veneer table top</li><li>Seats 4 people comfortably</li><li>Dirt and stain resistant surface</li></ul>',
            'tags': ['Modern Style', 'Solid Wood', 'Eco-friendly']
        },
        {
            'name': 'Ergonomic Mesh Office Chair',
            'category': 'Office Chairs',
            'price': 179.99,
            'description': 'Stay comfortable during long work hours. This chair features a breathable mesh back, adjustable lumbar support, and tilt function to keep your posture healthy.',
            'features': '<ul><li>Breathable mesh back</li><li>Adjustable height and tilt tension</li><li>Built-in lumbar support</li><li>Smooth-rolling casters</li></ul>',
            'tags': ['Industrial', 'Best Seller', 'Work From Home']
        },
        {
            'name': 'Industrial Metal Floor Lamp',
            'category': 'Lighting',
            'price': 69.99,
            'description': 'Add a touch of industrial style to your room with this oversized metal floor lamp. The adjustable head lets you direct light exactly where you need it.',
            'features': '<ul><li>Matte black metal finish</li><li>Adjustable lamp head</li><li>Foot switch for easy on/off</li><li>Compatible with LED bulbs</li></ul>',
            'tags': ['Industrial', 'Modern Style']
        },
        {
            'name': 'Soft Thick Pile Area Rug',
            'category': 'Home Decor',
            'price': 129.00,
            'description': 'Treat your feet to the softness of this thick pile rug. It dampens sound and adds a cozy feel to any room. Durable and stain-resistant synthetic fibers.',
            'features': '<ul><li>High pile for extra softness</li><li>Stain-resistant material</li><li>Sound dampening</li><li>Easy to vacuum</li></ul>',
            'tags': ['Modern Style', 'New Arrival', 'Cozy']
        },
        {
            'name': 'Lifelike Artificial Potted Plant',
            'category': 'Home Decor',
            'price': 12.99,
            'description': 'Enjoy the beauty of greenery without the maintenance. This lifelike artificial plant stays fresh year after year and looks great in any corner of your home.',
            'features': '<ul><li>Realistic appearance</li><li>No watering required</li><li>Includes black pot</li><li>Indoor/Outdoor use</li></ul>',
            'tags': ['Minimalist', 'Budget Friendly']
        },
        {
            'name': 'Bentwood Rocking Armchair',
            'category': 'Living Room Furniture',
            'price': 119.00,
            'description': 'A design icon for over 40 years. The bentwood frame is flexible yet strong, providing a gentle rocking motion that helps you relax.',
            'features': '<ul><li>Layer-glued bent birch frame</li><li>High back for neck support</li><li>Removable and washable cushion</li><li>Lightweight and durable</li></ul>',
            'tags': ['Classic', 'Best Seller', 'Comfort']
        },
        {
            'name': 'Compact Home Office Desk',
            'category': 'Tables & Desks',
            'price': 89.99,
            'description': 'A smart solution for small spaces. This compact desk features a cable outlet to keep cords organized and a storage unit that can be mounted on either side.',
            'features': '<ul><li>Integrated cable management</li><li>Reversible storage unit</li><li>Finished back (can be placed in middle of room)</li><li>Space-saving design</li></ul>',
            'tags': ['Modern Style', 'Minimalist', 'Student Favorite']
        },
        {
            'name': 'Luxury Velvet Accent Chair',
            'category': 'Living Room Furniture',
            'price': 299.00,
            'description': 'Add a splash of color and luxury to your room with this velvet accent chair. Soft to the touch with gold-finished metal legs.',
            'features': '<ul><li>Premium velvet upholstery</li><li>Gold-plated metal legs</li><li>High-density foam padding</li></ul>',
            'tags': ['Luxury', 'Modern Style', 'New Arrival']
        },
        {
            'name': 'Solid Wood Bedside Table',
            'category': 'Bedroom Furniture',
            'price': 49.99,
            'description': 'A simple and sturdy bedside table made from sustainable solid pine. Can be painted, oiled, or stained to match your decor.',
            'features': '<ul><li>Solid pine wood</li><li>Smooth running drawer</li><li>Sustainable material</li></ul>',
            'tags': ['Solid Wood', 'DIY Friendly', 'Eco-friendly']
        },
        {
            'name': 'Modern Pendant Light',
            'category': 'Lighting',
            'price': 39.99,
            'description': 'A stylish pendant lamp that provides directed light, perfect for dining tables or bar counters.',
            'features': '<ul><li>Modern design</li><li>Direct light</li><li>Easy height adjustment</li></ul>',
            'tags': ['Modern Style', 'Budget Friendly']
        }
    ]

    print("Creating products...")
    for p_data in products_data:
        # Find category
        cat_name = p_data['category']
        cat = category_map.get(cat_name)
        if not cat:
            # Fallback or create if missed
            cat = Category.objects.create(name=cat_name)
            category_map[cat_name] = cat
            
        product = Product.objects.create(
            name=p_data['name'],
            category=cat,
            price=Decimal(str(p_data['price'])),
            description=p_data['description'],
            features=p_data['features'],
            stock_quantity=random.randint(20, 150),
            thumbnail='https://via.placeholder.com/300x300?text=' + p_data['name'].replace(' ', '+'), 
            is_active=True
        )
        
        # Add tags
        for t_name in p_data.get('tags', []):
            tag = tag_map.get(t_name)
            if not tag:
                tag, _ = Tag.objects.get_or_create(name=t_name)
                tag_map[t_name] = tag
            ProductTag.objects.create(product=product, tag=tag)

        print(f"Created Product: {product.name}")

    print("Shop reset and population complete!")

if __name__ == '__main__':
    reset_and_populate()
