
import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from shop_app.models import Product, Category, Tag, ProductTag

def populate_data():
    print("Clearing existing products, categories, and tags...")
    Product.objects.all().delete()
    Category.objects.all().delete()
    Tag.objects.all().delete()

    # 1. Create Categories (Inspired by IKEA)
    categories_data = [
        'Sofas & Armchairs',
        'Beds & Mattresses',
        'Storage & Organization',
        'Tables & Desks',
        'Chairs',
        'Lighting',
        'Textiles',
        'Decoration'
    ]
    
    category_map = {}
    for cat_name in categories_data:
        cat = Category.objects.create(name=cat_name)
        category_map[cat_name] = cat
        print(f"Created Category: {cat_name}")

    # 2. Create Tags
    tags_data = [
        'New', 'Best Seller', 'Limited Offer', 'Sustainable', 
        'Modern', 'Classic', 'Minimalist', 'Industrial',
        'Handmade', 'Solid Wood', 'Metal', 'Glass'
    ]
    
    tag_map = {}
    for t_name in tags_data:
        tag = Tag.objects.create(name=t_name)
        tag_map[t_name] = tag
        print(f"Created Tag: {t_name}")

    # 3. Create Products
    products_data = [
        {
            'name': 'STRANDMON Wing Chair',
            'category': 'Sofas & Armchairs',
            'price': 249.00,
            'description': 'Bringing new life to an old favorite. We first introduced this chair in the 1950s. Some 60 years later we brought it back into the range with the same craftsmanship, comfort and appearance. Enjoy!',
            'features': '<ul><li>High back provides great support for your neck.</li><li>10 year guarantee.</li><li>Durable fabric cover.</li></ul>',
            'tags': ['Classic', 'Best Seller']
        },
        {
            'name': 'KIVIK 3-seat Sofa',
            'category': 'Sofas & Armchairs',
            'price': 599.00,
            'description': 'Cuddle up in the soft comfort of KIVIK sofa. The generous size, low armrests and memory foam that adapts to the contours of your body invites to many hours of naps, socializing and relaxation.',
            'features': '<ul><li>Memory foam adapts to your body.</li><li>Washable cover.</li><li>Low armrests.</li></ul>',
            'tags': ['Modern', 'New']
        },
        {
            'name': 'MALM Bed Frame',
            'category': 'Beds & Mattresses',
            'price': 229.00,
            'description': 'A clean design that’s just as beautiful on all sides – place the bed freestanding or with the headboard against a wall. If you need space for extra bedding, add MALM bed storage boxes on castors.',
            'features': '<ul><li>Adjustable bed sides allow you to use mattresses of different thicknesses.</li><li>Real wood veneer.</li></ul>',
            'tags': ['Minimalist', 'Best Seller']
        },
        {
            'name': 'BILLY Bookcase',
            'category': 'Storage & Organization',
            'price': 69.00,
            'description': 'It is estimated that every five seconds, one BILLY bookcase is sold somewhere in the world. Pretty impressive considering we launched BILLY in 1979. It’s the booklovers choice that never goes out of style.',
            'features': '<ul><li>Adjustable shelves.</li><li>Simple unit can be enough storage for a limited space or the foundation for a larger storage solution.</li></ul>',
            'tags': ['Classic', 'Best Seller', 'Sustainable']
        },
        {
            'name': 'KALLAX Shelf Unit',
            'category': 'Storage & Organization',
            'price': 44.99,
            'description': 'Standing or lying, against the wall or to divide the room – KALLAX series is eager to please and will adapt to your taste, space, budget and needs. Fine tune with drawers, shelves, boxes and inserts.',
            'features': '<ul><li>Choose whether you want to place it vertically or horizontally.</li><li>Easy to assemble.</li></ul>',
            'tags': ['Modern', 'Minimalist']
        },
        {
            'name': 'LISABO Table',
            'category': 'Tables & Desks',
            'price': 149.00,
            'description': 'Award-winning design and super easy to assemble. The table is strong, light and has a handcrafted look with a visible grain that gives each table a unique character.',
            'features': '<ul><li>Ash veneer top.</li><li>Solid birch legs.</li><li>Easy assembly.</li></ul>',
            'tags': ['Modern', 'Solid Wood', 'Award Winning']
        },
        {
            'name': 'MARKUS Office Chair',
            'category': 'Chairs',
            'price': 179.00,
            'description': 'Adjust the height and angle of this chair so your workday feels comfortable – the mesh backrest lets air through so you keep cool even when the workload rises. Built to outlast years of ups and downs.',
            'features': '<ul><li>10 year guarantee.</li><li>Adjustable height and tilt.</li><li>Mesh backrest for breathability.</li></ul>',
            'tags': ['Industrial', 'Best Seller']
        },
        {
            'name': 'HEKTAR Floor Lamp',
            'category': 'Lighting',
            'price': 69.99,
            'description': 'The simple, oversized metal shape is inspired by old lamps from places like factories and theaters. Used together, HEKTAR lamps support different activities and create a unified, rustic look in the room.',
            'features': '<ul><li>Adjustable head.</li><li>Oversized metal shade.</li><li>Industrial design.</li></ul>',
            'tags': ['Industrial', 'Metal']
        },
        {
            'name': 'RANGSTRUP Rug',
            'category': 'Textiles',
            'price': 129.00,
            'description': 'The dense, thick pile dampens sound and provides a soft surface to walk on. Durable, stain resistant and easy to care for since the rug is made of synthetic fibers.',
            'features': '<ul><li>Thick pile.</li><li>Stain resistant.</li><li>Sound dampening.</li></ul>',
            'tags': ['Modern', 'New']
        },
        {
            'name': 'FEJKA Artificial Plant',
            'category': 'Decoration',
            'price': 9.99,
            'description': 'FEJKA artificial potted plants that don’t require a green thumb. Perfect when you have better things to do than water plants and tidy up dead leaves. You’ll have everyone fooled because they look so lifelike.',
            'features': '<ul><li>Lifelike artificial plant.</li><li>Stays fresh year after year.</li></ul>',
            'tags': ['Minimalist']
        },
        {
            'name': 'POÄNG Armchair',
            'category': 'Sofas & Armchairs',
            'price': 119.00,
            'description': 'Timeless design and unmatched comfort have made POÄNG one of our most beloved armchairs for over 40 years.',
            'features': '<ul><li>Layer-glued bent wood frame.</li><li>High back support.</li><li>Washable cushion cover.</li></ul>',
            'tags': ['Classic', 'Best Seller', 'Sustainable']
        },
        {
            'name': 'MICKE Desk',
            'category': 'Tables & Desks',
            'price': 89.99,
            'description': 'A clean and simple look that fits just about anywhere. You can combine it with other desks or drawer units in the MICKE series to extend your work space.',
            'features': '<ul><li>Cable outlet at the back.</li><li>Storage unit can be mounted on right or left.</li></ul>',
            'tags': ['Modern', 'Minimalist', 'Best Seller']
        }
    ]

    print("Creating products...")
    for p_data in products_data:
        cat = category_map.get(p_data['category'])
        if not cat:
            print(f"Warning: Category {p_data['category']} not found for {p_data['name']}")
            continue
            
        product = Product.objects.create(
            name=p_data['name'],
            category=cat,
            price=p_data['price'],
            description=p_data['description'],
            features=p_data['features'],
            stock_quantity=random.randint(10, 100),
            thumbnail='https://via.placeholder.com/300x300?text=' + p_data['name'].replace(' ', '+'), # Placeholder
            is_active=True
        )
        
        # Add tags
        for t_name in p_data.get('tags', []):
            tag = tag_map.get(t_name)
            if tag:
                ProductTag.objects.create(product=product, tag=tag)
            elif t_name == 'Award Winning': # Dynamic creation for extra tags if needed
                 tag, _ = Tag.objects.get_or_create(name=t_name)
                 ProductTag.objects.create(product=product, tag=tag)

        print(f"Created Product: {product.name}")

    print("Data population complete!")

if __name__ == '__main__':
    populate_data()
