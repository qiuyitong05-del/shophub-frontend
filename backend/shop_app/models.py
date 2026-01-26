from django.db import models
from django.contrib.auth.models import AbstractUser

class ShopUser(AbstractUser):
    groups = models.ManyToManyField('auth.Group', related_name='shopuser_groups', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='shopuser_permissions', blank=True)
    email = models.EmailField(max_length=254, unique=True) 
    password_hash = models.CharField(max_length=128) 
    is_active = models.BooleanField(default=True)  

    class Meta:
        db_table = 'users_user'

class Address(models.Model):
    user = models.ForeignKey(ShopUser, on_delete=models.CASCADE, db_column='user_id')
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    detail_address = models.TextField()

    class Meta:
        db_table = 'users_address'

class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'products_category'

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    thumbnail = models.CharField(max_length=255) 
    description = models.TextField() 
    is_active = models.BooleanField(default=True) 
    category = models.ForeignKey(Category, on_delete=models.CASCADE, db_column='category_id')
    video_url = models.CharField(max_length=255, null=True, blank=True)
    stock_quantity = models.IntegerField(default=0)

    class Meta:
        db_table = 'products_product'

class ProductPhoto(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id')
    photo_url = models.CharField(max_length=255)

    class Meta:
        db_table = 'products_photo'

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id')
    user = models.ForeignKey(ShopUser, on_delete=models.CASCADE, db_column='user_id')
    rating = models.IntegerField() 
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    vendor_reply = models.TextField(null=True, blank=True)
    reply_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'products_review'
        unique_together = ('product', 'user') 

class ReviewPhoto(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, db_column='review_id')
    image_url = models.CharField(max_length=255)

    class Meta:
        db_table = 'reviews_photo'

class Order(models.Model):
    STATUS_CHOICES = (('Pending', 'Pending'), ('Hold', 'Hold'), ('Shipped', 'Shipped'), ('Cancelled', 'Cancelled'))
    user = models.ForeignKey(ShopUser, on_delete=models.CASCADE, db_column='user_id')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    shipped_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'orders_order'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='order_id')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id')
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2) 

    class Meta:
        db_table = 'orders_orderitem'

class CartItem(models.Model):
    user = models.ForeignKey(ShopUser, on_delete=models.CASCADE, db_column='user_id')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id')
    quantity = models.IntegerField(default=1)

    class Meta:
        db_table = 'cart_cartitem'

class Wishlist(models.Model):
    user = models.OneToOneField(ShopUser, on_delete=models.CASCADE, db_column='user_id')
    privacy = models.CharField(max_length=20, default='Private')
    share_token = models.CharField(max_length=100, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wishlists_wishlist'

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, db_column='wishlist_id')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wishlists_wishlistitem'
        unique_together = ('wishlist', 'product') 

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()

    class Meta:
        db_table = 'promotions_coupon'

class UserCoupon(models.Model):
    user = models.ForeignKey(ShopUser, on_delete=models.CASCADE, db_column='user_id')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, db_column='coupon_id')
    is_used = models.BooleanField(default=False)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'promotions_user_coupon'

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'tags_tag'

class ProductTag(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, db_column='tag_id')

    class Meta:
        db_table = 'products_product_tag'
        unique_together = ('product', 'tag')

class SearchHistory(models.Model):
    user = models.ForeignKey(ShopUser, on_delete=models.CASCADE, db_column='user_id', null=True)
    keyword = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'history_search'

class BrowseHistory(models.Model):
    user = models.ForeignKey(ShopUser, on_delete=models.CASCADE, db_column='user_id', null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id')
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'history_browse'

class Notification(models.Model):
    user = models.ForeignKey(ShopUser, on_delete=models.CASCADE, db_column='user_id')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=20)

    class Meta:
        db_table = 'notifications_notification'

class NotificationSetting(models.Model):
    user = models.OneToOneField(ShopUser, on_delete=models.CASCADE, db_column='user_id')
    master_switch = models.BooleanField(default=False)
    promo_on = models.BooleanField(default=False)
    stock_on = models.BooleanField(default=False)
    order_on = models.BooleanField(default=False)

    class Meta:
        db_table = 'users_notification_setting'