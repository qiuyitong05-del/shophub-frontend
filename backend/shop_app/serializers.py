from rest_framework import serializers
from .models import (
    ShopUser,
    Address,
    Product,
    ProductPhoto,
    CartItem,
    Order,
    OrderItem,
    Category,
)

class RegisterSerializer(serializers.ModelSerializer):
    province = serializers.CharField(write_only=True)
    city = serializers.CharField(write_only=True)
    detail_address = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    class Meta:
        model = ShopUser
        fields = ['username', 'email', 'password', 'password_confirm', 'province', 'city', 'detail_address']
        extra_kwargs = {'password': {'write_only': True}}
    def validate(self, data):
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({'password_confirm': ['两次输入的密码不一致']})
        return data
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        province = validated_data.pop('province')
        city = validated_data.pop('city')
        detail_address = validated_data.pop('detail_address')
        user = ShopUser.objects.create_user(**validated_data)
        Address.objects.create(user=user, province=province, city=city, detail_address=detail_address)
        return user

class ProductPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPhoto
        fields = ['id', 'photo_url']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import Tag
        model = Tag
        fields = ['id', 'name']

class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_id = serializers.IntegerField(source='category.id', read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'thumbnail', 'category_name', 'category_id', 'stock_quantity']

class ProductDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    photos = ProductPhotoSerializer(source='productphoto_set', many=True, read_only=True)
    tags = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'thumbnail', 'description', 'stock_quantity', 'photos', 'video_url', 'category_name', 'features', 'tags', 'width', 'height', 'depth', 'is_customizable']

    def get_tags(self, obj):
        return [t.tag.name for t in obj.producttag_set.all()]

class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_thumbnail = serializers.CharField(source='product.thumbnail', read_only=True)
    unit_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = CartItem
        fields = ['product_id', 'product_name', 'product_thumbnail', 'unit_price', 'quantity', 'custom_dimensions']

class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_thumbnail = serializers.CharField(source='product.thumbnail', read_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    has_review = serializers.SerializerMethodField()
    next_review_stage = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'product_name', 'product_thumbnail', 'unit_price', 'quantity', 'has_review', 'custom_dimensions', 'next_review_stage']
        
    def get_has_review(self, obj):
        # Check if instant review exists
        return obj.reviews.exists()

    def get_next_review_stage(self, obj):
        # Calculate days since order created
        from django.utils import timezone
        if not obj.order.created_at:
            return None
        days_diff = (timezone.now() - obj.order.created_at).days
        
        # Stages: 30, 60, 120, 360
        # Check in reverse order to find the latest eligible stage
        stages = [360, 120, 60, 30]
        for stage in stages:
            if days_diff >= stage:
                # Check if long-term review exists for this stage
                if not obj.long_term_reviews.filter(stage=stage).exists():
                    return stage
        return None


class OrderListSerializer(serializers.ModelSerializer):
    coupon_code = serializers.CharField(source='coupon.code', read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'status', 'total_amount', 'created_at', 'shipped_at', 'cancelled_at', 'discount_amount', 'coupon_code']

class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)
    coupon_code = serializers.CharField(source='coupon.code', read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'status', 'total_amount', 'shipping_address', 'shipped_at', 'cancelled_at', 'created_at', 'items', 'user_id', 'discount_amount', 'coupon_code']

class ReviewPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import ReviewPhoto
        model = ReviewPhoto
        fields = ['id', 'image_url']

class LongTermReviewPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import LongTermReviewPhoto
        model = LongTermReviewPhoto
        fields = ['id', 'image_url']

class ReviewFollowUpSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import ReviewFollowUp
        model = ReviewFollowUp
        fields = ['id', 'comment', 'created_at']

class AnswerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        from .models import Answer
        model = Answer
        fields = ['id', 'user', 'username', 'content', 'is_merchant_reply', 'created_at']
        read_only_fields = ['user', 'is_merchant_reply', 'created_at']

class QuestionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    class Meta:
        from .models import Question
        model = Question
        fields = ['id', 'product', 'user', 'username', 'content', 'tag', 'created_at', 'answers']
        read_only_fields = ['user', 'created_at']

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    photos = ReviewPhotoSerializer(source='reviewphoto_set', many=True, read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_thumbnail = serializers.CharField(source='product.thumbnail', read_only=True)
    followups = ReviewFollowUpSerializer(many=True, read_only=True)
    helpful_count = serializers.SerializerMethodField()
    unhelpful_count = serializers.SerializerMethodField()
    user_vote = serializers.SerializerMethodField()
    
    class Meta:
        from .models import Review
        model = Review
        fields = ['id', 'product', 'user', 'username', 'rating', 'rating_logistics', 'rating_service', 'comment', 'created_at', 'vendor_reply', 'reply_at', 'photos', 'product_name', 'product_thumbnail', 'order_item', 'edit_count', 'followups', 'helpful_count', 'unhelpful_count', 'user_vote', 'is_anonymous']
        read_only_fields = ['user', 'created_at', 'vendor_reply', 'reply_at', 'product_name', 'product_thumbnail', 'edit_count']

    def validate_comment(self, value):
        from .utils import contains_profanity
        if contains_profanity(value):
            raise serializers.ValidationError("Comment contains inappropriate language.")
        return value

    def get_username(self, obj):
        if obj.is_anonymous:
            name = obj.user.username
            if len(name) > 2:
                return f"{name[0]}***{name[-1]}"
            else:
                return f"{name[0]}***"
        return obj.user.username

    def get_helpful_count(self, obj):
        return obj.votes.filter(vote_type='helpful').count()

    def get_unhelpful_count(self, obj):
        return obj.votes.filter(vote_type='unhelpful').count()

    def get_user_vote(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from .models import ReviewVote
            try:
                vote = ReviewVote.objects.get(review=obj, user=request.user)
                return vote.vote_type
            except ReviewVote.DoesNotExist:
                return None
        return None

class LongTermReviewSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    photos = LongTermReviewPhotoSerializer(many=True, read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_thumbnail = serializers.CharField(source='product.thumbnail', read_only=True)
    
    class Meta:
        from .models import LongTermReview
        model = LongTermReview
        fields = ['id', 'product', 'user', 'username', 'rating', 'comment', 'created_at', 'vendor_reply', 'reply_at', 'photos', 'product_name', 'product_thumbnail', 'order_item', 'stage', 'is_anonymous']
        read_only_fields = ['user', 'created_at', 'vendor_reply', 'reply_at', 'product_name', 'product_thumbnail']
        
    def validate_comment(self, value):
        from .utils import contains_profanity
        if contains_profanity(value):
            raise serializers.ValidationError("Comment contains inappropriate language.")
        return value

    def get_username(self, obj):
        if obj.is_anonymous:
            name = obj.user.username
            if len(name) > 2:
                return f"{name[0]}***{name[-1]}"
            else:
                return f"{name[0]}***"
        return obj.user.username

class AdminProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'thumbnail', 'is_active']

class AdminProductDetailSerializer(serializers.ModelSerializer):
    photos = ProductPhotoSerializer(source='productphoto_set', many=True, read_only=True)
    category_id = serializers.IntegerField(source='category.id', read_only=True)
    tags = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'thumbnail', 'description', 'stock_quantity', 'is_active', 'photos', 'video_url', 'category_id', 'features', 'tags']
    def get_tags(self, obj):
        return [t.tag.name for t in obj.producttag_set.all()]

class AdminProductSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True, required=True)
    tags = serializers.CharField(write_only=True, required=False, allow_blank=True)
    class Meta:
        model = Product
        fields = ['name', 'price', 'thumbnail', 'description', 'stock_quantity', 'is_active', 'category_id', 'video_url', 'features', 'tags', 'width', 'height', 'depth', 'is_customizable']
    def create(self, validated_data):
        category_id = validated_data.pop('category_id')
        tags_str = validated_data.pop('tags', '')
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            raise serializers.ValidationError({'category_id': '分类不存在'})
        product = Product.objects.create(category=category, **validated_data)
        
        # Handle tags
        if tags_str:
            from .models import Tag, ProductTag
            tag_names = [t.strip() for t in tags_str.split(',') if t.strip()]
            for t_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=t_name)
                ProductTag.objects.create(product=product, tag=tag)
                
        return product
    def update(self, instance, validated_data):
        category_id = validated_data.pop('category_id', None)
        tags_str = validated_data.pop('tags', None)
        
        if category_id is not None:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                raise serializers.ValidationError({'category_id': '分类不存在'})
            instance.category = category
        
        for field in ['name', 'price', 'thumbnail', 'description', 'stock_quantity', 'is_active', 'video_url', 'features', 'width', 'height', 'depth', 'is_customizable']:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        
        # Update tags if provided
        if tags_str is not None:
            from .models import Tag, ProductTag
            # Clear existing
            instance.producttag_set.all().delete()
            tag_names = [t.strip() for t in tags_str.split(',') if t.strip()]
            for t_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=t_name)
                ProductTag.objects.create(product=instance, tag=tag)
                
        return instance

class AdminOrderListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'status', 'total_amount', 'created_at', 'username', 'user_id', 'shipped_at', 'cancelled_at']

class WishlistItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_thumbnail = serializers.CharField(source='product.thumbnail', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    stock_quantity = serializers.IntegerField(source='product.stock_quantity', read_only=True)
    price_drop = serializers.SerializerMethodField()
    
    class Meta:
        from .models import WishlistItem
        model = WishlistItem
        fields = ['id', 'product', 'product_name', 'product_thumbnail', 'product_price', 'added_at', 'price_at_addition', 'price_drop', 'stock_quantity']

    def get_price_drop(self, obj):
        current_price = obj.product.price
        if obj.price_at_addition > current_price:
            return obj.price_at_addition - current_price
        return 0

class WishlistSerializer(serializers.ModelSerializer):
    items = WishlistItemSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        from .models import Wishlist
        model = Wishlist
        fields = ['id', 'user', 'username', 'privacy', 'share_token', 'items', 'created_at']

class NotificationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import NotificationSetting
        model = NotificationSetting
        fields = ['master_switch', 'promotion_on', 'invitation_on', 'price_drop_on', 'restock_on', 'order_update_on']

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    is_sender_me = serializers.SerializerMethodField()
    
    class Meta:
        from .models import Message
        model = Message
        fields = ['id', 'sender', 'sender_name', 'receiver', 'content', 'is_read', 'created_at', 'is_sender_me']
        read_only_fields = ['sender', 'created_at']

    def get_is_sender_me(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.sender == request.user
        return False

# 在 AdminOrderListSerializer 类后面添加
class AdminOrderDetailSerializer(serializers.ModelSerializer):
    """管理员端订单详情序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)  # 复用已有的OrderItemSerializer
    
    class Meta:
        model = Order
        fields = [
            'id', 'status', 'total_amount', 'created_at', 'shipped_at', 
            'cancelled_at', 'username', 'user_id', 'shipping_address', 'items'
        ]
        read_only_fields = ['user_id', 'created_at', 'shipped_at', 'cancelled_at']