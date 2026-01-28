from django.contrib import admin
from .models import (
    ShopUser, Address, Category, Product, ProductPhoto, 
    Review, ReviewPhoto, Order, OrderItem, CartItem, 
    Wishlist, WishlistItem, Coupon, UserCoupon, Tag, 
    ProductTag, SearchHistory, BrowseHistory, Notification, NotificationSetting
)

@admin.register(ShopUser)
class ShopUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active') # 后台列表显示的列 [cite: 173-193]
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock_quantity', 'is_active', 'category') # [cite: 215-251]
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock_quantity', 'is_active')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__username')
    readonly_fields = ('created_at',) 

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at') 
    list_filter = ('rating', 'created_at')

other_models = [
    Address, Category, ProductPhoto, ReviewPhoto, 
    OrderItem, CartItem, Wishlist, WishlistItem, Coupon, 
    UserCoupon, Tag, ProductTag, SearchHistory, BrowseHistory, 
    Notification, NotificationSetting
]

admin.site.register(other_models)
