from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction, models
from django.db.models import Case, When, Value, IntegerField, CharField
from django.db.models.functions import Cast

# ... existing imports ...

from decimal import Decimal
from .models import Product, CartItem, Order, OrderItem, ProductPhoto, Category, Address, Review, ShopUser
from .serializers import (
    RegisterSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    CartItemSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    AdminProductListSerializer,
    AdminProductDetailSerializer,
    AdminProductSerializer,
    AdminOrderListSerializer,
    AdminOrderDetailSerializer,
    CategorySerializer,
    ReviewSerializer,
    ReviewPhotoSerializer,
    QuestionSerializer,
    AnswerSerializer,
    ReviewFollowUpSerializer,
    WishlistSerializer,
    WishlistItemSerializer,
    LongTermReviewSerializer
)

def create_notification_if_allowed(user, message, category, product=None, order_item=None):
    from .models import NotificationSetting, Notification
    setting, _ = NotificationSetting.objects.get_or_create(user=user)
    
    if not setting.master_switch:
        return
        
    allowed = False
    if category == 'promotion' and setting.promotion_on:
        # Admins don't need promotion notifications
        if user.is_staff:
            allowed = False
        else:
            allowed = True
    elif category == 'invitation' and setting.invitation_on:
        allowed = True
    elif category == 'price_drop' and setting.price_drop_on:
        # Admins don't need price drop notifications
        if user.is_staff:
            allowed = False
        else:
            allowed = True
    elif category == 'restock' and setting.restock_on:
        allowed = True
    elif category == 'order_update' and setting.order_update_on:
        allowed = True
        
    if allowed:
        Notification.objects.create(
            user=user,
            message=message,
            category=category,
            product=product,
            order_item=order_item
        )

@api_view(['GET'])
def get_wishlist(request):
    user_id = request.query_params.get('user_id')
    share_token = request.query_params.get('share_token')
    
    if share_token:
        # Public access
        from .models import Wishlist
        wishlist = get_object_or_404(Wishlist, share_token=share_token)
        if wishlist.privacy == 'Private' and str(wishlist.user.id) != str(user_id):
             return Response({'error': 'This wishlist is private'}, status=status.HTTP_403_FORBIDDEN)
    elif user_id:
        # User access
        from .models import Wishlist
        import uuid
        wishlist, _ = Wishlist.objects.get_or_create(user_id=user_id)
        # Ensure token exists
        if not wishlist.share_token:
            wishlist.share_token = uuid.uuid4().hex
            wishlist.save()
    else:
        return Response({'error': 'User ID or Token required'}, status=status.HTTP_400_BAD_REQUEST)

    # Filter/Sort
    sort_by = request.query_params.get('sort') # price_drop, in_stock
    
    items = list(wishlist.items.all())
    
    # Python-level sorting/filtering for computed properties
    if sort_by == 'price_drop':
        # Sort by price difference (current < initial)
        items = sorted(items, key=lambda x: max(0, x.price_at_addition - x.product.price), reverse=True)
    elif sort_by == 'in_stock':
        # Stock > 0 first
        items = sorted(items, key=lambda x: x.product.stock_quantity > 0, reverse=True)
    else:
        # Default sort by added_at desc
        items = sorted(items, key=lambda x: x.added_at, reverse=True)

    w_data = WishlistSerializer(wishlist).data
    # Override items with sorted list
    w_data['items'] = WishlistItemSerializer(items, many=True).data
    
    return Response(w_data, status=status.HTTP_200_OK)

@api_view(['POST'])
def add_to_wishlist(request):
    user_id = request.data.get('user_id')
    product_id = request.data.get('product_id')
    
    if not user_id or not product_id:
        return Response({'error': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)
        
    from .models import Wishlist, WishlistItem, Notification
    wishlist, _ = Wishlist.objects.get_or_create(user_id=user_id)
    product = get_object_or_404(Product, id=product_id)
    
    item, created = WishlistItem.objects.get_or_create(
        wishlist=wishlist, 
        product=product,
        defaults={'price_at_addition': product.price}
    )
    
    # U6: Stock Replenishment Notification (Initial check if added when OOS)
    # If user adds OOS item, they implicitly subscribe.
    # We can handle the notification trigger when stock is updated (admin_update_product or checkout cancellation)
    
    if not created:
        return Response({'message': 'Already in wishlist'}, status=status.HTTP_200_OK)
        
    return Response({'message': 'Added to wishlist'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def remove_from_wishlist(request):
    user_id = request.data.get('user_id')
    product_id = request.data.get('product_id')
    
    if not user_id or not product_id:
        return Response({'error': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)
        
    from .models import Wishlist, WishlistItem
    try:
        wishlist = Wishlist.objects.get(user_id=user_id)
        WishlistItem.objects.filter(wishlist=wishlist, product_id=product_id).delete()
    except Wishlist.DoesNotExist:
        pass
        
    return Response({'message': 'Removed'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def update_wishlist_privacy(request):
    user_id = request.data.get('user_id')
    privacy = request.data.get('privacy') # Private/Public
    
    if not user_id or privacy not in ['Private', 'Public']:
        return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
        
    from .models import Wishlist
    import uuid
    wishlist, _ = Wishlist.objects.get_or_create(user_id=user_id)
    wishlist.privacy = privacy
    if privacy == 'Public' and not wishlist.share_token:
        wishlist.share_token = uuid.uuid4().hex
    wishlist.save()
    
    return Response(WishlistSerializer(wishlist).data, status=status.HTTP_200_OK)

@api_view(['POST'])
def wishlist_bulk_add_to_cart(request):
    user_id = request.data.get('user_id')
    product_ids = request.data.get('product_ids') # List
    
    if not user_id or not product_ids:
        return Response({'error': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)
        
    # Reuse add_to_cart logic or bulk create
    # Let's iterate for simplicity and stock check
    results = []
    for pid in product_ids:
        # Mock request data for add_to_cart
        # But calling view directly is messy. Use logic.
        product = get_object_or_404(Product, id=pid)
        if product.stock_quantity > 0:
            item, _ = CartItem.objects.get_or_create(
                user_id=user_id, 
                product=product, 
                custom_dimensions='', # Explicitly set empty dimensions to match add_to_cart default
                defaults={'quantity': 0}
            )
            if item.quantity + 1 <= product.stock_quantity:
                item.quantity += 1
                item.save()
                results.append(f"Added {product.name}")
            else:
                results.append(f"Stock limit for {product.name}")
        else:
            results.append(f"Out of stock: {product.name}")
            
    return Response({'results': results}, status=status.HTTP_200_OK)

@api_view(['POST'])
def create_review(request):
    user_id = request.data.get('user_id')
    order_item_id = request.data.get('order_item_id')
    
    if not user_id or not order_item_id:
        return Response({'error': 'Missing user_id or order_item_id'}, status=status.HTTP_400_BAD_REQUEST)
        
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    
    # Check if user owns the order
    if order_item.order.user_id != int(user_id):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
    # Check if already reviewed (Instant)
    if order_item.reviews.exists():
        return Response({'error': 'This item has already been reviewed.'}, status=status.HTTP_400_BAD_REQUEST)

    data = request.data.copy()
    data['product'] = order_item.product.id
    data['user'] = user_id
    data['order_item'] = order_item_id
    
    serializer = ReviewSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        # Pass user explicitly since it's read_only in serializer
        review = serializer.save(user_id=user_id)
        
        # T3: Handle photos
        photos = request.data.get('photos', []) # List of URLs
        from .models import ReviewPhoto
        for url in photos:
            if url:
                ReviewPhoto.objects.create(review=review, image_url=url)
                
        # Coupon issuance removed for instant reviews as per new requirement

        # Re-serialize to include photos
        return Response(ReviewSerializer(review, context={'request': request}).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_long_term_review(request):
    user_id = request.data.get('user_id')
    order_item_id = request.data.get('order_item_id')
    stage = int(request.data.get('stage', 0))
    
    if not user_id or not order_item_id or not stage:
        return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
        
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    
    # Check if user owns the order
    if order_item.order.user_id != int(user_id):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    # Check eligibility (X14)
    from django.utils import timezone
    days_diff = (timezone.now() - order_item.order.created_at).days
    if days_diff < stage:
        return Response({'error': f'Not yet eligible for {stage}-day review'}, status=status.HTTP_400_BAD_REQUEST)
        
    # Check if already exists (X15)
    from .models import LongTermReview
    if LongTermReview.objects.filter(order_item=order_item, stage=stage).exists():
        return Response({'error': 'Already reviewed for this stage'}, status=status.HTTP_400_BAD_REQUEST)

    data = request.data.copy()
    data['product'] = order_item.product.id
    data['user'] = user_id
    data['order_item'] = order_item_id
    data['stage'] = stage
    
    serializer = LongTermReviewSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        review = serializer.save(user_id=user_id)
        
        # Handle photos
        photos = request.data.get('photos', [])
        from .models import LongTermReviewPhoto
        for url in photos:
            if url:
                LongTermReviewPhoto.objects.create(review=review, image_url=url)
                
        # Issue $15 coupon for long-term review (Req 6)
        from .models import Coupon, UserCoupon, Notification
        import uuid
        code = f"LTR-{stage}D-{uuid.uuid4().hex[:6].upper()}"
        # Unlimited validity
        valid_until = timezone.now() + timezone.timedelta(days=36500)
        
        coupon, _ = Coupon.objects.get_or_create(code=code, defaults={
            'discount_amount': 15.00,
            'valid_from': timezone.now(),
            'valid_until': valid_until
        })
        UserCoupon.objects.create(user_id=user_id, coupon=coupon)
        
        create_notification_if_allowed(
            user=ShopUser.objects.get(id=user_id),
            message=f"Thanks for your {stage}-day review! You received a $15 coupon: {code}",
            category="promotion",
            product=review.product
        )

        return Response(LongTermReviewSerializer(review, context={'request': request}).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def edit_long_term_review(request, review_id):
    from .models import LongTermReview
    from .serializers import LongTermReviewSerializer
    review = get_object_or_404(LongTermReview, id=review_id)
    
    # Check authorization
    user_id = request.data.get('user_id')
    if str(review.user.id) != str(user_id):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    # Allow partial update: only rating, comment, is_anonymous should be updated
    # Stage and product info are fixed
    serializer = LongTermReviewSerializer(review, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        review = serializer.save()
        
        # Handle photos update (Replace logic: clear old, add new)
        photos = request.data.get('photos')
        if photos is not None:
            from .models import LongTermReviewPhoto
            review.photos.all().delete()
            for url in photos:
                if url:
                    LongTermReviewPhoto.objects.create(review=review, image_url=url)

        return Response(LongTermReviewSerializer(review, context={'request': request}).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    # Check authorization
    user_id = request.data.get('user_id')
    if str(review.user.id) != str(user_id):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    # T1: Limit to 1 edit
    if review.edit_count >= 1:
        return Response({'error': 'You can only edit your review once.'}, status=status.HTTP_400_BAD_REQUEST)

    # Allow partial update: only comment, rating. Photos should NOT be changed for ordinary reviews per rules.
    # We will ignore 'photos' from request data.
    data_to_update = {}
    if 'comment' in request.data:
        data_to_update['comment'] = request.data['comment']
    if 'rating' in request.data:
        data_to_update['rating'] = request.data['rating']
        
    serializer = ReviewSerializer(review, data=data_to_update, partial=True, context={'request': request})
    if serializer.is_valid():
        review = serializer.save()
        review.edit_count += 1
        review.save()

        # Photos are NOT allowed to be replaced for edited ordinary reviews
        # Removing the photo replacement logic completely

        return Response(ReviewSerializer(review, context={'request': request}).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    # Check authorization (assuming passed in body or header, here body for consistency)
    user_id = request.data.get('user_id')
    # Or query param
    if not user_id:
        user_id = request.query_params.get('user_id')
        
    if str(review.user.id) != str(user_id):
        # Allow admin delete too? For now just owner.
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    # Due to cascading delete, ReviewVote objects are deleted automatically,
    # resetting the helpful vote count. The user can create a new review because
    # order_item.reviews.exists() will be false.
    review.delete()
    return Response({'message': 'Review deleted'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def add_review_followup(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    user_id = request.data.get('user_id')
    if str(review.user.id) != str(user_id):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
    comment = request.data.get('comment')
    if not comment:
        return Response({'error': 'Comment is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    from .models import ReviewFollowUp
    from .utils import contains_profanity
    if contains_profanity(comment):
        return Response({'error': 'Comment contains inappropriate language'}, status=status.HTTP_400_BAD_REQUEST)

    ReviewFollowUp.objects.create(review=review, comment=comment)
    return Response(ReviewSerializer(review, context={'request': request}).data, status=status.HTTP_200_OK)

@api_view(['POST'])
def vote_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    user_id = request.data.get('user_id')
    vote_type = request.data.get('vote_type') # helpful/unhelpful
    
    if not user_id:
        return Response({'error': 'User ID required'}, status=status.HTTP_400_BAD_REQUEST)
        
    # Prevent self-voting to avoid malicious vote farming
    if str(review.user.id) == str(user_id):
        return Response({'error': 'You cannot vote on your own review'}, status=status.HTTP_400_BAD_REQUEST)
        
    if vote_type not in ['helpful', 'unhelpful']:
        return Response({'error': 'Invalid vote type'}, status=status.HTTP_400_BAD_REQUEST)
        
    from .models import ReviewVote
    
    # Check if exists
    try:
        with transaction.atomic():
            try:
                vote = ReviewVote.objects.select_for_update().get(user_id=user_id, review=review)
                if vote.vote_type == vote_type:
                    # Toggle off (remove vote)
                    vote.delete()
                else:
                    # Change vote
                    vote.vote_type = vote_type
                    vote.save()
            except ReviewVote.DoesNotExist:
                ReviewVote.objects.create(user_id=user_id, review=review, vote_type=vote_type)
            
            # Check for $5 reward threshold
            # We need to refresh the review from db to get accurate counts inside transaction
            review.refresh_from_db()
            helpful_count = review.votes.filter(vote_type='helpful').count()
            reward_message = None
            if helpful_count >= 5 and not review.helpful_reward_issued:
                # Issue reward
                from .models import Coupon, UserCoupon
                import uuid
                
                # Ensure we have a $5 no-threshold coupon template
                try:
                    from django.utils import timezone
                    import datetime
                    coupon, _ = Coupon.objects.get_or_create(
                        code='HELPFUL_REVIEW_5',
                        defaults={
                            'discount_amount': Decimal('5.00'),
                            'valid_from': timezone.now(),
                            'valid_until': timezone.now() + datetime.timedelta(days=36500)
                        }
                    )
                except Coupon.MultipleObjectsReturned:
                    coupon = Coupon.objects.filter(code='HELPFUL_REVIEW_5').first()
                    
                user_coupon_code = f"THX-{uuid.uuid4().hex[:8].upper()}"
                UserCoupon.objects.create(
                    user=review.user,
                    coupon=coupon
                    # Removed code parameter as it's not in the model
                )
                
                review.helpful_reward_issued = True
                review.save()
                
                # Send Notification
                create_notification_if_allowed(
                    user=review.user,
                    message="Your review was very helpful! We have issued a $5 no-threshold coupon to your account as a reward.",
                    category='promotion',
                    product=review.product
                )
                reward_message = "Vote recorded. A $5 coupon was issued to the author for their helpful review!"
    except Exception as e:
        print(f"Error in vote_review: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    response_data = ReviewSerializer(review, context={'request': request}).data
    # Return as an object with message if rewarded
    if reward_message:
        # Inject message into response_data so frontend easily accesses res.message
        response_data['message'] = reward_message
        return Response(response_data, status=status.HTTP_200_OK)
    
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def product_reviews(request, product_id):
    sort_by = request.query_params.get('sort', 'helpful')
    review_type = request.query_params.get('type', 'instant') # instant or long_term
    
    # Import serializers here to avoid NameError if not imported at top
    from .serializers import ReviewSerializer, LongTermReviewSerializer
    
    if review_type == 'long_term':
        from .models import LongTermReview
        qs = LongTermReview.objects.filter(product_id=product_id)
        serializer_class = LongTermReviewSerializer
    else:
        qs = Review.objects.filter(product_id=product_id)
        serializer_class = ReviewSerializer
    
    # Sort
    if sort_by == 'newest':
        qs = qs.order_by('-created_at')
    elif sort_by == 'highest':
        qs = qs.order_by('-rating')
    elif sort_by == 'lowest':
        qs = qs.order_by('rating')
    elif sort_by == 'helpful':
        # Helpful logic differs for LongTerm?
        # For now, Review has helpful_votes annotation.
        # LongTermReview doesn't have ReviewVote model support yet?
        # User didn't specify voting for long-term. Let's skip helpful sort for long-term or add support.
        # Assuming simple sort for now or just created_at.
        if review_type == 'long_term':
            qs = qs.order_by('-created_at')
        else:
            from django.db.models import Count, Q
            qs = qs.annotate(
                helpful_votes=Count('votes', filter=Q(votes__vote_type='helpful'))
            ).order_by('-helpful_votes', '-created_at')
        
    serializer = serializer_class(qs, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)

# Q&A APIs
@api_view(['GET'])
def product_questions(request, product_id):
    from .models import Question
    qs = Question.objects.filter(product_id=product_id).order_by('-created_at')
    serializer = QuestionSerializer(qs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def create_question(request):
    user_id = request.data.get('user_id')
    product_id = request.data.get('product_id')
    content = request.data.get('content')
    tag = request.data.get('tag') # seller/buyer
    
    if not all([user_id, product_id, content, tag]):
        return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
        
    from .models import Question, Notification, ShopUser
    # Profanity check
    from .utils import contains_profanity
    if contains_profanity(content):
        return Response({'error': 'Content contains inappropriate language'}, status=status.HTTP_400_BAD_REQUEST)

    question = Question.objects.create(user_id=user_id, product_id=product_id, content=content, tag=tag)
    
    # Notifications
    if tag == 'seller':
        # Notify Admins
        admins = ShopUser.objects.filter(is_staff=True)
        for admin in admins:
            create_notification_if_allowed(
                user=admin,
                message=f"New question for seller on {question.product.name}: {content[:30]}...",
                category="invitation",
                product=question.product
            )
            
    elif tag == 'buyer':
        # Notify Buyers (shipped orders)
        # Find users who bought this product and have 'Shipped' status
        buyer_ids = OrderItem.objects.filter(
            product_id=product_id, 
            order__status='Shipped'
        ).values_list('order__user_id', flat=True).distinct()
        
        buyers = ShopUser.objects.filter(id__in=buyer_ids)
        for bid_user in buyers:
            # Don't notify self
            if bid_user.id != int(user_id):
                create_notification_if_allowed(
                    user=bid_user,
                    message=f"Someone asked a question about {question.product.name}: {content[:30]}... Can you help?",
                    category="invitation",
                    product=question.product
                )

    return Response(QuestionSerializer(question).data, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
def delete_question(request, question_id):
    from .models import Question
    question = get_object_or_404(Question, id=question_id)
    user_id = request.query_params.get('user_id')
    
    if not user_id:
        # Try auth user
        if request.user.is_authenticated:
            user_id = request.user.id
        else:
            return Response({'error': 'User ID required'}, status=status.HTTP_400_BAD_REQUEST)
            
    # Check if user is owner or admin
    if str(question.user.id) != str(user_id) and not request.user.is_staff:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
    question.delete()
    return Response({'message': 'Question deleted'}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_answer(request, answer_id):
    from .models import Answer
    answer = get_object_or_404(Answer, id=answer_id)
    user_id = request.query_params.get('user_id')
    
    if not user_id:
        if request.user.is_authenticated:
            user_id = request.user.id
        else:
            return Response({'error': 'User ID required'}, status=status.HTTP_400_BAD_REQUEST)
            
    if str(answer.user.id) != str(user_id) and not request.user.is_staff:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    # Requirement: Answerer can only modify, not delete.
    if not request.user.is_staff and str(answer.user.id) == str(user_id):
         return Response({'error': 'You can only modify your answer, not delete it.'}, status=status.HTTP_403_FORBIDDEN)
        
    answer.delete()
    return Response({'message': 'Answer deleted'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def edit_answer(request, answer_id):
    from .models import Answer
    answer = get_object_or_404(Answer, id=answer_id)
    user_id = request.data.get('user_id')
    content = request.data.get('content')
    
    if not user_id or not content:
        return Response({'error': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)
        
    if str(answer.user.id) != str(user_id):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
    # Profanity check
    from .utils import contains_profanity
    if contains_profanity(content):
        return Response({'error': 'Content contains inappropriate language'}, status=status.HTTP_400_BAD_REQUEST)
        
    answer.content = content
    answer.save()
    return Response(AnswerSerializer(answer).data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_notifications(request):
    user_id = request.query_params.get('user_id')
    if not user_id:
        return Response({'error': 'User ID required'}, status=status.HTTP_400_BAD_REQUEST)
    
    from .models import ShopUser
    # Check and generate review invitations (Req 6)
    try:
        user = ShopUser.objects.get(id=user_id)
        check_review_invitations(user)
    except ShopUser.DoesNotExist:
        pass
    
    from .models import Notification
    qs = Notification.objects.filter(user_id=user_id).order_by('-created_at')
    # Simple serialization
    data = [{'id': n.id, 'message': n.message, 'category': n.category, 'is_read': n.is_read, 'created_at': n.created_at, 'product_id': n.product.id if n.product else None, 'product_name': n.product.name if n.product else None, 'order_item_id': n.order_item.id if n.order_item else None, 'order_id': n.order_item.order.id if n.order_item else None} for n in qs]
    return Response(data, status=status.HTTP_200_OK)

def check_review_invitations(user):
    from .models import OrderItem, Notification, NotificationSetting
    
    # Check settings
    try:
        setting = NotificationSetting.objects.get(user=user)
        if not setting.master_switch or not setting.invitation_on:
             return
    except NotificationSetting.DoesNotExist:
        pass # Default True
    
    # Get all items from shipped orders
    # Req: "after order shipped" -> use shipped_at
    # We need to filter items where order.shipped_at is not null
    items = OrderItem.objects.filter(order__user=user, order__status='Shipped', order__shipped_at__isnull=False)
    
    # Req 6: 30d, 60d, 120d, 360d
    stages = [30, 60, 120, 360]
    
    for item in items:
        if not item.order.shipped_at: continue
        days_diff = (timezone.now() - item.order.shipped_at).days
        
        for stage in stages:
            if days_diff >= stage:
                # Check if already reviewed for this stage
                if item.long_term_reviews.filter(stage=stage).exists():
                    continue
                    
                # Check if notification already sent
                if Notification.objects.filter(
                    user=user, 
                    category='invitation', 
                    order_item=item,
                    message__contains=f"{stage}-day"
                ).exists():
                    continue
                    
                Notification.objects.create(
                    user=user,
                    message=f"Time for your {stage}-day review of {item.product.name}! Share your experience and get a $15 coupon.",
                    category='invitation',
                    order_item=item,
                    product=item.product
                )

@api_view(['POST'])
def mark_notification_read(request, notification_id):
    from .models import Notification
    try:
        n = Notification.objects.get(id=notification_id)
        n.is_read = True
        n.save()
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)
    except Notification.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def create_answer(request, question_id):
    user_id = request.data.get('user_id')
    content = request.data.get('content')
    
    if not user_id or not content:
        return Response({'error': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)
        
    from .models import Question, Answer, ShopUser
    question = get_object_or_404(Question, id=question_id)
    
    # Profanity check
    from .utils import contains_profanity
    if contains_profanity(content):
        return Response({'error': 'Content contains inappropriate language'}, status=status.HTTP_400_BAD_REQUEST)

    is_merchant = False
    # Check logic
    # Ensure user_id is int
    try:
        user = ShopUser.objects.get(id=int(user_id))
    except (ValueError, ShopUser.DoesNotExist):
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if question.tag == 'seller':
        if not user.is_staff:
             return Response({'error': 'Only seller can answer this question'}, status=status.HTTP_403_FORBIDDEN)
        is_merchant = True
    else:
        # Ask Buyers: Check if user bought product AND order is Shipped
        has_bought = OrderItem.objects.filter(product=question.product, order__user=user, order__status='Shipped').exists()
        if not has_bought and not user.is_staff:
           return Response({'error': 'Only buyers who have received the item can answer.'}, status=status.HTTP_403_FORBIDDEN)
        
    answer = Answer.objects.create(question=question, user=user, content=content, is_merchant_reply=is_merchant)
    
    # Reward Coupon (T3)
    if question.tag == 'buyer':
        # Create coupon logic (One per user per question)
        from .models import Coupon, UserCoupon, Notification
        
        previous_answers = Answer.objects.filter(question=question, user=user).exclude(id=answer.id)
        if not previous_answers.exists():
            import uuid
            code = f"ANS-{uuid.uuid4().hex[:6].upper()}"
            # Unlimited validity (Req 5)
            valid_until = timezone.now() + timezone.timedelta(days=36500)
            
            coupon, _ = Coupon.objects.get_or_create(code=code, defaults={
                'discount_amount': 5.00,
                'valid_from': timezone.now(),
                'valid_until': valid_until
            })
            UserCoupon.objects.create(user=user, coupon=coupon)
            # Notify user
            create_notification_if_allowed(
                user=user,
                message=f"Thanks for your help! You received a $5 coupon: {code}",
                category="promotion",
                product=question.product
            )
            return Response({'message': 'Answer posted! You received a $5 coupon.', 'answer': AnswerSerializer(answer).data}, status=status.HTTP_201_CREATED)
        else:
             return Response({'message': 'Answer posted! (Coupon limit reached for this question)', 'answer': AnswerSerializer(answer).data}, status=status.HTTP_201_CREATED)

    return Response(AnswerSerializer(answer).data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def admin_all_reviews(request):
    qs = Review.objects.all().order_by('-created_at')
    serializer = ReviewSerializer(qs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def admin_reply_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    reply = request.data.get('reply')
    
    if not reply:
        return Response({'error': 'Reply content is required'}, status=status.HTTP_400_BAD_REQUEST)
        
    review.vendor_reply = reply
    review.reply_at = timezone.now()
    review.save()
    
    return Response(ReviewSerializer(review).data, status=status.HTTP_200_OK)

@api_view(['GET'])
def category_list(request):
    qs = Category.objects.all().order_by('id')
    serializer = CategorySerializer(qs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

@api_view(['POST'])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Registration successful!'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        if user.is_staff:
            return Response({'error': 'Admin account must log in via the admin site.'}, status=status.HTTP_403_FORBIDDEN)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key, 
            'user_id': user.id, 
            'username': user.username,
            'is_staff': user.is_staff
        }, status=status.HTTP_200_OK)
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def admin_login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        if not user.is_staff:
            return Response({'error': 'Access denied. Not an admin account.'}, status=status.HTTP_403_FORBIDDEN)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'is_staff': user.is_staff
        }, status=status.HTTP_200_OK)
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def product_list(request):
    q = (request.query_params.get('q') or '').strip()
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    category_ids = request.query_params.get('category_ids')
    min_price = request.query_params.get('min_price')
    max_price = request.query_params.get('max_price')
    tags_param = request.query_params.get('tags')
    sort = (request.query_params.get('sort') or '').strip()

    qs = Product.objects.filter(is_active=True)

    if q:
        from django.db import models as djmodels
        
        # U10: Record search history
        user = request.user if request.user.is_authenticated else None
        from .models import SearchHistory
        SearchHistory.objects.create(user=user, keyword=q[:255])

        # Only search name (User requirement 1)
        # Split query by spaces to allow partial match of multiple terms (subset match)
        terms = q.split()
        if len(terms) > 1:
            for term in terms:
                # Use AND logic for strict subset match (e.g., "Modern Light" matches "Modern Pendant Light")
                qs = qs.filter(name__icontains=term)
        else:
            qs = qs.filter(name__icontains=q)

    if category_ids:
        ids = [int(x) for x in category_ids.split(',') if x.isdigit()]
        if ids:
            qs = qs.filter(category_id__in=ids)

    if min_price:
        qs = qs.filter(price__gte=min_price)
    if max_price:
        qs = qs.filter(price__lte=max_price)

    if tags_param:
        tags = [t.strip() for t in tags_param.split(',') if t.strip()]
        if tags:
            qs = qs.filter(producttag__tag__name__in=tags)

    if sort == 'price_asc':
        qs = qs.order_by('price', 'id')
    elif sort == 'price_desc':
        qs = qs.order_by('-price', '-id')
    else:
        qs = qs.order_by('-id')

    qs = qs.distinct()

    paginator = Paginator(qs, page_size)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    serializer = ProductListSerializer(items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def product_detail(request, pk: int):
    product = get_object_or_404(Product, id=pk)
    
    # U10: Record Browse History
    if request.user.is_authenticated:
        from .models import BrowseHistory
        # Update timestamp if exists, or create new
        # For simplicity, just create new entries to track frequency, 
        # but admin analytics usually wants 'latest view'. 
        # Let's update existing or create.
        BrowseHistory.objects.update_or_create(
            user=request.user, 
            product=product,
            defaults={'viewed_at': timezone.now()}
        )
        
    serializer = ProductDetailSerializer(product)
    
    # Get related products (C4)
    # Logic: Same category, exclude self. Order randomly to vary recommendations if there are many. Take up to 4.
    related_qs = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id).order_by('?')[:4]
    related_products = list(related_qs)
    
    # If not enough, maybe add some with same tags?
    if len(related_products) < 4:
        tag_ids = product.producttag_set.values_list('tag_id', flat=True)
        if tag_ids:
            count_needed = 4 - len(related_products)
            existing_ids = [p.id for p in related_products] + [product.id]
            more_related = Product.objects.filter(producttag__tag__id__in=tag_ids, is_active=True).exclude(id__in=existing_ids).order_by('?').distinct()[:count_needed]
            # Combine
            related_products.extend(list(more_related))
            
    related_serializer = ProductListSerializer(related_products, many=True)
    
    data = serializer.data
    data['related_products'] = related_serializer.data
    
    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
def add_to_cart(request):
    user_id = request.data.get('user_id')
    product_id = request.data.get('product_id')
    quantity = int(request.data.get('quantity', 1))
    custom_dimensions = request.data.get('custom_dimensions', '')

    if not user_id or not product_id:
        return Response({'error': 'User ID and Product ID are required'}, status=status.HTTP_400_BAD_REQUEST)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if quantity > product.stock_quantity:
        return Response({'error': f'Insufficient stock. Only {product.stock_quantity} left.'}, status=status.HTTP_400_BAD_REQUEST)

    # Handle merging of items with empty/null dimensions
    if not custom_dimensions:
        # Try to find existing item with empty or null dimensions
        item = CartItem.objects.filter(
            user_id=user_id,
            product=product
        ).filter(models.Q(custom_dimensions='') | models.Q(custom_dimensions__isnull=True)).first()
        
        if item:
            # Normalize to empty string if needed
            if item.custom_dimensions is None:
                item.custom_dimensions = ''
                item.save()
        else:
            item = CartItem.objects.create(
                user_id=user_id, 
                product=product, 
                custom_dimensions='',
                quantity=0
            )
    else:
        # Use custom_dimensions in get_or_create to separate items with different dimensions
        item, created = CartItem.objects.get_or_create(
            user_id=user_id, 
            product=product, 
            custom_dimensions=custom_dimensions,
            defaults={'quantity': 0}
        )

    if item.quantity + quantity > product.stock_quantity:
        return Response({'error': f'Insufficient stock. Only {product.stock_quantity} left.'}, status=status.HTTP_400_BAD_REQUEST)
        
    item.quantity += quantity
    item.save()
    serializer = CartItemSerializer(item)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_available_coupons(request):
    user_id = request.query_params.get('user_id')
    if not user_id:
        return Response({'error': 'User ID required'}, status=status.HTTP_400_BAD_REQUEST)
        
    from .models import UserCoupon
    # Get unused, valid coupons
    ucs = UserCoupon.objects.filter(
        user_id=user_id, 
        is_used=False, 
        coupon__valid_until__gte=timezone.now()
    ).select_related('coupon').order_by('-coupon__discount_amount')
    
    data = []
    for uc in ucs:
        data.append({
            'user_coupon_id': uc.id,
            'code': uc.coupon.code,
            'discount_amount': uc.coupon.discount_amount,
            'valid_until': uc.coupon.valid_until
        })
        
    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
def move_to_wishlist(request):
    user_id = request.data.get('user_id')
    product_id = request.data.get('product_id')
    
    if not user_id or not product_id:
        return Response({'error': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)
        
    from .models import Wishlist, WishlistItem, CartItem, Product
    
    try:
        with transaction.atomic():
            # Add to wishlist
            wishlist, _ = Wishlist.objects.get_or_create(user_id=user_id)
            product = get_object_or_404(Product, id=product_id)
            
            WishlistItem.objects.get_or_create(
                wishlist=wishlist, 
                product=product,
                defaults={'price_at_addition': product.price}
            )
            
            # Remove from cart (all quantities of this product)
            CartItem.objects.filter(user_id=user_id, product_id=product_id).delete()
            
        return Response({'message': 'Moved to wishlist'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_cart_recommendations(request):
    user_id = request.query_params.get('user_id')
    if not user_id:
        return Response({'error': 'User ID required'}, status=status.HTTP_400_BAD_REQUEST)
        
    from .models import WishlistItem
    # Get items from wishlist sorted by price ASC, excluding out of stock
    items = WishlistItem.objects.filter(wishlist__user_id=user_id, product__stock_quantity__gt=0).select_related('product').order_by('product__price')
    
    data = []
    for item in items:
        p = item.product
        data.append({
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'thumbnail': p.thumbnail,
            'stock': p.stock_quantity
        })
            
    return Response(data, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def find_similar_products(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Logic: Same category, exclude self, take up to 4
    related_qs = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]
    related_products = list(related_qs)
    
    # If not enough, add same tags
    if len(related_products) < 4:
        tag_ids = product.producttag_set.values_list('tag_id', flat=True)
        if tag_ids:
            count_needed = 4 - len(related_products)
            existing_ids = [p.id for p in related_products] + [product.id]
            more_related = Product.objects.filter(producttag__tag__id__in=tag_ids, is_active=True).exclude(id__in=existing_ids).distinct()[:count_needed]
            related_products.extend(list(more_related))
            
    serializer = ProductListSerializer(related_products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_user_product_review_eligibility(request, product_id):
    user_id = request.query_params.get('user_id')
    if not user_id:
        return Response({'error': 'User ID required'}, status=status.HTTP_400_BAD_REQUEST)
        
    from .models import OrderItem, LongTermReview
    # Find shipped orders for this product
    items = OrderItem.objects.filter(
        product_id=product_id, 
        order__user_id=user_id, 
        order__status='Shipped',
        order__shipped_at__isnull=False
    ).order_by('-order__shipped_at')
    
    if not items.exists():
        return Response({'eligible': False}, status=status.HTTP_200_OK)
        
    # Pick the most recent item
    item = items.first()
    days_diff = (timezone.now() - item.order.shipped_at).days
    
    stages = [30, 60, 120, 360]
    available_stages = []
    for s in stages:
        if days_diff >= s:
            # Check if already reviewed for this stage
            if not LongTermReview.objects.filter(order_item=item, stage=s).exists():
                available_stages.append(s)
    
    # User requirement: "if 30d not reviewed and it's 60d, 30d changes to 60d"
    # This means we only show the LATEST available stage
    latest_stage = available_stages[-1] if available_stages else None
    
    return Response({
        'eligible': True,
        'order_item_id': item.id,
        'days_owned': days_diff,
        'available_stage': latest_stage
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_cart(request):
    user_id = request.query_params.get('user_id')
    if not user_id:
        return Response({'error': 'user_id必填'}, status=status.HTTP_400_BAD_REQUEST)
    items = CartItem.objects.filter(user_id=user_id)
    serializer = CartItemSerializer(items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def update_cart_item(request):
    user_id = request.data.get('user_id')
    product_id = request.data.get('product_id')
    quantity = int(request.data.get('quantity', 1))
    if not user_id or not product_id:
        return Response({'error': 'user_id和product_id必填'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        item = CartItem.objects.get(user_id=user_id, product_id=product_id)
    except CartItem.DoesNotExist:
        return Response({'error': '购物车项不存在'}, status=status.HTTP_404_NOT_FOUND)
    if quantity <= 0:
        item.delete()
        return Response({'message': '已删除'}, status=status.HTTP_200_OK)
    item.quantity = quantity
    item.save()
    serializer = CartItemSerializer(item)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def remove_from_cart(request):
    user_id = request.data.get('user_id')
    product_id = request.data.get('product_id')
    if not user_id or not product_id:
        return Response({'error': 'user_id和product_id必填'}, status=status.HTTP_400_BAD_REQUEST)
    deleted, _ = CartItem.objects.filter(user_id=user_id, product_id=product_id).delete()
    if deleted == 0:
        return Response({'error': '购物车项不存在'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'message': '已删除'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def checkout(request):
    user_id = request.data.get('user_id')
    shipping_address = request.data.get('shipping_address', '')
    selected_ids = request.data.get('selected_ids')  # List of product_ids
    user_coupon_id = request.data.get('user_coupon_id') # New

    if not user_id:
        return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    qs = CartItem.objects.select_related('product').filter(user_id=user_id)
    if selected_ids is not None:
        # If selected_ids is provided (even if empty list), filter by it
        qs = qs.filter(product_id__in=selected_ids)
    
    items = list(qs)
    if not items:
        return Response({'error': 'No items selected for checkout'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 检查库存
    for it in items:
        if it.quantity > it.product.stock_quantity:
            return Response({'error': f'Insufficient stock for {it.product.name}. Only {it.product.stock_quantity} left.'}, status=status.HTTP_400_BAD_REQUEST)

    total = Decimal('0.00')
    for it in items:
        total += it.product.price * it.quantity
        
    # Coupon logic
    discount = Decimal('0.00')
    used_coupon = None
    if user_coupon_id:
        from .models import UserCoupon
        try:
            uc = UserCoupon.objects.get(id=user_coupon_id, user_id=user_id, is_used=False)
            if uc.coupon.valid_until >= timezone.now():
                discount = uc.coupon.discount_amount
                used_coupon = uc.coupon
            else:
                 return Response({'error': 'Coupon expired'}, status=status.HTTP_400_BAD_REQUEST)
        except UserCoupon.DoesNotExist:
             return Response({'error': 'Invalid coupon'}, status=status.HTTP_400_BAD_REQUEST)

    # Apply shipping fee if total < 999
    # User requirement: shipping logic remains
    shipping_fee = Decimal('0.00')
    if total < 999:
        shipping_fee = Decimal('20.00')
        
    final_total = total + shipping_fee - discount
    if final_total < 0:
        final_total = Decimal('0.00')
        
    with transaction.atomic():
        # 扣减库存
        for it in items:
            product = it.product
            # 使用 select_for_update 锁住行，防止并发问题
            product = Product.objects.select_for_update().get(id=product.id)
            if product.stock_quantity < it.quantity:
                raise Exception(f'Insufficient stock for {product.name}')
            product.stock_quantity -= it.quantity
            product.save()

        order = Order.objects.create(
            user_id=user_id, 
            status='Pending', 
            total_amount=final_total, 
            shipping_address=shipping_address,
            coupon=used_coupon,
            discount_amount=discount
        )
        
        # Mark coupon used
        if user_coupon_id:
            uc = UserCoupon.objects.get(id=user_coupon_id)
            uc.is_used = True
            uc.save()

        bulk = []
        for it in items:
            bulk.append(OrderItem(
                order=order, 
                product=it.product, 
                quantity=it.quantity, 
                unit_price=it.product.price,
                custom_dimensions=it.custom_dimensions
            ))
        OrderItem.objects.bulk_create(bulk)
        
        # Only delete purchased items
        # We can use the IDs from the items list we just processed
        purchased_ids = [it.id for it in items] # Use CartItem IDs
        CartItem.objects.filter(id__in=purchased_ids).delete()

        # Notify Admins about new order
        admins = ShopUser.objects.filter(is_staff=True)
        first_item = order.orderitem_set.first()
        for admin in admins:
            create_notification_if_allowed(
                user=admin,
                message=f"New Order #{order.id} placed by {order.user.username}!",
                category="order_update",
                order_item=first_item
            )

    serializer = OrderDetailSerializer(order)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def orders_list(request):
    user_id = request.query_params.get('user_id')
    status_q = request.query_params.get('status')
    order_id = request.query_params.get('order_id')
    
    qs = Order.objects.all()
    if user_id:
        qs = qs.filter(user_id=user_id)
    if status_q:
        qs = qs.filter(status=status_q)
    if order_id:
        qs = qs.filter(id=order_id)
        
    qs = qs.order_by('-created_at')
    serializer = OrderListSerializer(qs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def default_address(request):
    user_id = request.query_params.get('user_id')
    if not user_id and request.user.is_authenticated:
        user_id = request.user.id
        
    if not user_id:
        return Response({'address': ''}, status=status.HTTP_200_OK)
        
    addr = Address.objects.filter(user_id=user_id).first()
    if not addr:
        return Response({'address': ''}, status=status.HTTP_200_OK)
    full = f"{addr.province} {addr.city} {addr.detail_address}".strip()
    return Response({'address': full}, status=status.HTTP_200_OK)

@api_view(['GET'])
def order_detail(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    serializer = OrderDetailSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def cancel_order(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    if order.status == 'Shipped':
        return Response({'error': 'Cannot cancel shipped order'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 如果订单状态已经是Cancelled，则不处理，避免重复增加库存
    if order.status == 'Cancelled':
         return Response({'message': 'Order already cancelled'}, status=status.HTTP_200_OK)

    with transaction.atomic():
        order.status = 'Cancelled'
        order.cancelled_at = timezone.now()
        order.save()
        
        # 恢复库存
        items = OrderItem.objects.filter(order=order)
        for item in items:
            product = item.product
            product.stock_quantity += item.quantity
            product.save()
            
        # Notification: Order Cancelled
        create_notification_if_allowed(
            user=order.user,
            message=f"Order #{order.id} has been cancelled.",
            category="order_update",
            product=items.first().product if items.exists() else None,
            order_item=items.first() if items.exists() else None
        )
        
        # Notify Admins about cancelled order
        admins = ShopUser.objects.filter(is_staff=True)
        for admin in admins:
            create_notification_if_allowed(
                user=admin,
                message=f"Order #{order.id} cancelled by customer!",
                category="order_update",
                order_item=items.first() if items.exists() else None
            )

    serializer = OrderDetailSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def admin_products(request):
    qs = Product.objects.all().order_by('-id')
    q = request.query_params.get('q')
    if q:
        q = q.strip()
        from django.db import models as djmodels
        
        # Admin search logic also improved to support subset/fuzzy match
        terms = q.split()
        if len(terms) > 1:
            for term in terms:
                sub_cond = (djmodels.Q(name__icontains=term) |
                            djmodels.Q(description__icontains=term))
                qs = qs.filter(sub_cond)
        else:
             qs = qs.filter(models.Q(name__icontains=q) | models.Q(description__icontains=q))
             
        if q.isdigit():
             # If exact ID match or fuzzy text match
             qs = qs.filter(models.Q(id=int(q)) | models.Q(name__icontains=q) | models.Q(description__icontains=q))

    serializer = AdminProductListSerializer(qs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def admin_product_detail(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    serializer = AdminProductDetailSerializer(product)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def admin_create_product(request):
    data = request.data.copy()
    # Auto-add thumbnail to photos if not present
    if data.get('thumbnail') and 'photos' not in data:
         # If using frontend logic to add photos separately, this might be tricky.
         # But usually AdminProductSerializer doesn't handle photos directly.
         pass

    serializer = AdminProductSerializer(data=data)
    if serializer.is_valid():
        product = serializer.save()
        
        # Auto-add thumbnail as the first photo
        if product.thumbnail:
            from .models import ProductPhoto
            # Check if exists
            if not ProductPhoto.objects.filter(product=product, photo_url=product.thumbnail).exists():
                ProductPhoto.objects.create(product=product, photo_url=product.thumbnail)
        
        detail = AdminProductDetailSerializer(product)
        return Response(detail.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def admin_update_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    old_price = product.price
    old_stock = product.stock_quantity
    
    serializer = AdminProductSerializer(product, data=request.data, partial=True)
    if serializer.is_valid():
        product = serializer.save()
        
        # Auto-add thumbnail as a photo if updated/set
        if product.thumbnail:
            from .models import ProductPhoto
            if not ProductPhoto.objects.filter(product=product, photo_url=product.thumbnail).exists():
                 ProductPhoto.objects.create(product=product, photo_url=product.thumbnail)

        # U5: Price Drop Notification
        if product.price < old_price:
            # Find users who have this in wishlist
            from .models import WishlistItem, Notification
            items = WishlistItem.objects.filter(product=product)
            for item in items:
                # Notify user
                create_notification_if_allowed(
                    user=item.wishlist.user,
                    message=f"Price Drop! {product.name} is now ${product.price} (was ${old_price})",
                    category="price_drop",
                    product=product
                )

        # U6: Stock Replenishment Notification
        if old_stock <= 0 and product.stock_quantity > 0:
            from .models import WishlistItem, Notification
            items = WishlistItem.objects.filter(product=product)
            for item in items:
                create_notification_if_allowed(
                    user=item.wishlist.user,
                    message=f"Back in Stock! {product.name} is now available.",
                    category="restock",
                    product=product
                )

        detail = AdminProductDetailSerializer(product)
        return Response(detail.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def admin_disable_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    product.is_active = False
    product.save()
    detail = AdminProductDetailSerializer(product)
    return Response(detail.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def admin_enable_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    product.is_active = True
    product.save()
    detail = AdminProductDetailSerializer(product)
    return Response(detail.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def admin_orders(request):
    qs = Order.objects.all()
    
    # Base ordering
    ordering = []
    
    # Filter by user_id (Fuzzy search + Priority sort)
    user_id_input = request.query_params.get('user_id')
    if user_id_input:
        # Cast user_id to string for substring search
        qs = qs.annotate(user_id_str=Cast('user_id', output_field=CharField()))
        qs = qs.filter(user_id_str__icontains=user_id_input)
        
        # Sort exact match first
        try:
            uid_int = int(user_id_input)
            qs = qs.annotate(
                user_match_priority=Case(
                    When(user_id=uid_int, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField()
                )
            )
            ordering.append('user_match_priority')
        except ValueError:
            pass
        
    # Filter by username
    username = request.query_params.get('username')
    if username:
        qs = qs.filter(user__username__icontains=username)
        
    # Filter by order_id (Fuzzy search + Priority sort)
    order_id_input = request.query_params.get('order_id')
    if order_id_input:
        qs = qs.annotate(order_id_str=Cast('id', output_field=CharField()))
        qs = qs.filter(order_id_str__icontains=order_id_input)
        
        try:
            oid_int = int(order_id_input)
            qs = qs.annotate(
                order_match_priority=Case(
                    When(id=oid_int, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField()
                )
            )
            ordering.append('order_match_priority')
        except ValueError:
            pass
        
    # Filter by status
    status_q = request.query_params.get('status')
    if status_q:
        qs = qs.filter(status=status_q)
    
    # Apply ordering
    ordering.append('-created_at')
    qs = qs.order_by(*ordering)
    
    # Pagination
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 10))
    paginator = Paginator(qs, page_size)
    
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
        
    serializer = AdminOrderListSerializer(items, many=True)
    return Response({
        'results': serializer.data,
        'total': paginator.count,
        'page': page,
        'page_size': page_size,
        'total_pages': paginator.num_pages
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def admin_order_detail(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    serializer = AdminOrderDetailSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def admin_add_product_photo(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    photo_url = request.data.get('photo_url')
    
    # Check if file upload
    if request.FILES.get('photo_file'):
        photo_file = request.FILES['photo_file']
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        
        file_path = default_storage.save(f'product_photos/{photo_file.name}', ContentFile(photo_file.read()))
        # Build full URL
        photo_url = request.build_absolute_uri(default_storage.url(file_path))

    if not photo_url:
        return Response({'error': 'Photo URL or File is required'}, status=status.HTTP_400_BAD_REQUEST)
        
    photo = ProductPhoto.objects.create(product=product, photo_url=photo_url)
    return Response({'id': photo.id, 'photo_url': photo.photo_url}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def admin_remove_product_photo(request, product_id: int, photo_id: int):
    product = get_object_or_404(Product, id=product_id)
    try:
        photo = ProductPhoto.objects.get(id=photo_id, product=product)
    except ProductPhoto.DoesNotExist:
        return Response({'error': '照片不存在'}, status=status.HTTP_404_NOT_FOUND)
    photo.delete()
    return Response({'message': '已删除'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def update_order_status(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    status_val = request.data.get('status')
    valid = ['Pending', 'Hold', 'Shipped', 'Cancelled']
    if status_val not in valid:
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
    
    with transaction.atomic():
        # 如果从非Cancelled变更为Cancelled，需要恢复库存
        if order.status != 'Cancelled' and status_val == 'Cancelled':
            items = OrderItem.objects.filter(order=order)
            for item in items:
                item.product.stock_quantity += item.quantity
                item.product.save()
        
        # 如果从Cancelled变更为非Cancelled，需要扣减库存
        if order.status == 'Cancelled' and status_val != 'Cancelled':
             items = OrderItem.objects.filter(order=order)
             for item in items:
                if item.product.stock_quantity < item.quantity:
                     return Response({'error': f'Insufficient stock for {item.product.name}, cannot restore order'}, status=status.HTTP_400_BAD_REQUEST)
                item.product.stock_quantity -= item.quantity
                item.product.save()

        order.status = status_val
        if status_val == 'Shipped':
            order.shipped_at = timezone.now()
        if status_val == 'Cancelled':
            order.cancelled_at = timezone.now()
        order.save()
        
        # Notification
        first_item = OrderItem.objects.filter(order=order).select_related('product').first()
        create_notification_if_allowed(
            user=order.user,
            message=f"Order #{order.id} status update: {status_val}",
            category="order_update",
            product=first_item.product if first_item else None,
            order_item=first_item
        )

        # Check for stockouts if Shipped (Notify Vendor)
        if status_val == 'Shipped':
            items = OrderItem.objects.filter(order=order)
            out_of_stock_items = []
            for item in items:
                if item.product.stock_quantity <= 0:
                    out_of_stock_items.append(item.product)
                    
            if out_of_stock_items:
                admins = ShopUser.objects.filter(is_staff=True)
                for admin in admins:
                    for prod in out_of_stock_items:
                        create_notification_if_allowed(
                            user=admin,
                            message=f"Stock Alert: {prod.name} is out of stock! Please restock.",
                            category="restock",
                            product=prod
                        )
        
    serializer = OrderDetailSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def admin_ship_order(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'Shipped'
    order.shipped_at = timezone.now()
    order.save()
    
    # Notification
    first_item = order.orderitem_set.select_related('product').first()
    create_notification_if_allowed(
        user=order.user,
        message=f"Order #{order.id} has been shipped!",
        category="order_update",
        product=first_item.product if first_item else None,
        order_item=first_item
    )
    
    # Check for stockouts (Notify Vendor)
    items = order.orderitem_set.all()
    out_of_stock_items = []
    for item in items:
        if item.product.stock_quantity <= 0:
            out_of_stock_items.append(item.product)
            
    if out_of_stock_items:
        admins = ShopUser.objects.filter(is_staff=True)
        for admin in admins:
            for prod in out_of_stock_items:
                create_notification_if_allowed(
                    user=admin,
                    message=f"Stock Alert: {prod.name} is out of stock! Please restock.",
                    category="restock",
                    product=prod
                )

    serializer = OrderDetailSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def admin_hold_order(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'Hold'
    order.save()
    
    # Notification
    first_item = order.orderitem_set.select_related('product').first()
    create_notification_if_allowed(
        user=order.user,
        message=f"Order #{order.id} is on Hold.",
        category="order_update",
        product=first_item.product if first_item else None,
        order_item=first_item
    )
    
    serializer = OrderDetailSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def upload_image(request):
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    
    # Use a generic uploads directory
    file_path = default_storage.save(f'uploads/{file.name}', ContentFile(file.read()))
    full_url = request.build_absolute_uri(default_storage.url(file_path))
    
    return Response({'url': full_url}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def admin_search_analytics(request):
    from .models import SearchHistory, Product
    from django.db.models import Count
    # U10: Aggregated search data
    # Get top 20 search terms
    qs = SearchHistory.objects.values('keyword').annotate(count=Count('keyword')).order_by('-count')[:20]
    
    data = []
    for item in qs:
        keyword = item['keyword']
        count = item['count']
        
        # Try to find a matching product (best effort)
        # Use simple icontains match. If multiple, pick first.
        matching_product = Product.objects.filter(name__icontains=keyword).first()
        
        data.append({
            'keyword': keyword,
            'count': count,
            'product_id': matching_product.id if matching_product else None,
            'product_name': matching_product.name if matching_product else None
        })
        
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
def admin_wishlist_analytics(request):
    # U12: Wish List Popularity Rank
    from django.db.models import Count
    from .models import Product
    
    # Products most frequently added to wishlists
    qs = Product.objects.annotate(wishlist_count=Count('wishlistitem')).order_by('-wishlist_count')[:20]
    
    # Serialize manually or create a small serializer
    data = []
    for p in qs:
        data.append({
            'id': p.id,
            'name': p.name,
            'wishlist_count': p.wishlist_count,
            'price': p.price,
            'stock': p.stock_quantity
        })
        
    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
def admin_issue_wishlist_coupon(request):
    # U11: Issue coupon to users who have specific product in wishlist
    product_id = request.data.get('product_id')
    discount_amount = request.data.get('discount_amount', 5.00)
    days_valid = request.data.get('days_valid', 7)
    
    if not product_id:
        return Response({'error': 'Product ID required'}, status=status.HTTP_400_BAD_REQUEST)
        
    from .models import WishlistItem, Coupon, UserCoupon, Notification
    import uuid
    
    # Find users
    items = WishlistItem.objects.filter(product_id=product_id)
    if not items.exists():
        return Response({'message': 'No users have this item in wishlist'}, status=status.HTTP_200_OK)
        
    # Create a generic coupon or unique coupons? 
    # Let's create one coupon code for this campaign but assign individually
    code = f"WISH-{product_id}-{uuid.uuid4().hex[:6].upper()}"
    coupon = Coupon.objects.create(
        code=code,
        discount_amount=discount_amount,
        valid_from=timezone.now(),
        valid_until=timezone.now() + timezone.timedelta(days=int(days_valid))
    )
    
    count = 0
    for item in items:
        user = item.wishlist.user
        # Avoid duplicate coupons for same campaign if run multiple times?
        # For simplicity, just issue.
        UserCoupon.objects.create(user=user, coupon=coupon)
        
        # Notify user
        create_notification_if_allowed(
            user=user,
            message=f"Special Offer! You liked {item.product.name}. Here is a ${discount_amount} coupon: {code}. Valid until {coupon.valid_until.date().isoformat()}.",
            category="promotion",
            product=item.product
        )
        count += 1
        
    return Response({'message': f'Coupons issued to {count} users'}, status=status.HTTP_200_OK)
        
@api_view(['GET'])
def get_notification_settings(request):
    user = request.user
    if not user.is_authenticated:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    
    from .models import NotificationSetting
    from .serializers import NotificationSettingSerializer
    settings, _ = NotificationSetting.objects.get_or_create(user=user)
    return Response(NotificationSettingSerializer(settings).data, status=status.HTTP_200_OK)

@api_view(['POST'])
def update_notification_settings(request):
    user = request.user
    if not user.is_authenticated:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
    from .models import NotificationSetting
    from .serializers import NotificationSettingSerializer
    settings, _ = NotificationSetting.objects.get_or_create(user=user)
    
    serializer = NotificationSettingSerializer(settings, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_messages(request):
    # X10: Private Chat Messages
    user = request.user
    if not user.is_authenticated:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    
    target_user_id = request.query_params.get('target_user_id')
    
    from .models import Message, ShopUser
    from .serializers import MessageSerializer
    from django.db.models import Q
    
    if user.is_staff:
        # Merchant view
        if not target_user_id:
            return Response({'error': 'Target user ID required for merchant'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Admin should see messages between this user and ANY staff member (or the specific one)
        # Assuming shared inbox for all staff:
        qs = Message.objects.filter(
            (Q(sender_id=target_user_id) & Q(receiver__is_staff=True)) |
            (Q(sender__is_staff=True) & Q(receiver_id=target_user_id))
        ).order_by('created_at')
        
        # Mark as read
        Message.objects.filter(
            sender_id=target_user_id,
            receiver__is_staff=True,
            is_read=False
        ).update(is_read=True)
        
    else:
        # Customer view
        qs = Message.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).order_by('created_at')
        
        # Mark as read
        Message.objects.filter(
            receiver=user,
            is_read=False
        ).update(is_read=True)
        
    serializer = MessageSerializer(qs, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def send_message(request):
    user = request.user
    if not user.is_authenticated:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
    content = request.data.get('content')
    if not content:
        return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)
        
    # X4: Profanity filter
    from .utils import contains_profanity
    if contains_profanity(content):
        return Response({'error': 'Send failure: Content contains inappropriate language.'}, status=status.HTTP_400_BAD_REQUEST)
        
    from .models import Message, ShopUser
    
    # Determine receiver
    if user.is_staff:
        receiver_id = request.data.get('receiver_id')
        if not receiver_id:
            return Response({'error': 'Receiver ID required'}, status=status.HTTP_400_BAD_REQUEST)
        receiver = get_object_or_404(ShopUser, id=receiver_id)
    else:
        # Customer sending to Merchant.
        # Pick a staff member. Ideally the one who replied last, or a default one.
        # For simplicity, pick the first superuser or staff.
        receiver = ShopUser.objects.filter(is_staff=True).first()
        if not receiver:
             return Response({'error': 'No customer service available'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
             
    msg = Message.objects.create(sender=user, receiver=receiver, content=content)
    
    # Return formatted message
    from .serializers import MessageSerializer
    return Response(MessageSerializer(msg, context={'request': request}).data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def admin_chat_conversations(request):
    # Helper to list users who have chatted with merchant
    if not request.user.is_staff:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
    from .models import Message
    
    # Get all distinct users from messages involving this staff (or any staff if we want shared inbox)
    # We want all customers who sent a message to any staff OR received a message from any staff
    
    # Get list of users who are NOT staff but have messages
    customer_ids = set(Message.objects.filter(sender__is_staff=False).values_list('sender_id', flat=True))
    customer_ids.update(set(Message.objects.filter(receiver__is_staff=False).values_list('receiver_id', flat=True)))
    
    from django.db.models import Q
    from .models import ShopUser
    customers = ShopUser.objects.filter(id__in=customer_ids)
    
    data = []
    for c in customers:
        # Get last message
        last_msg = Message.objects.filter(
            (Q(sender=c) & Q(receiver__is_staff=True)) |
            (Q(sender__is_staff=True) & Q(receiver=c))
        ).order_by('-created_at').first()
        
        unread_count = Message.objects.filter(
            sender=c,
            receiver__is_staff=True,
            is_read=False
        ).count()
        
        data.append({
            'user_id': c.id,
            'username': c.username,
            'last_message': last_msg.content if last_msg else '',
            'last_time': last_msg.created_at if last_msg else None,
            'unread_count': unread_count
        })
        
    from django.utils import timezone
    # Sort by last time
    data.sort(key=lambda x: x['last_time'] or timezone.now(), reverse=True)
    
    return Response(data, status=status.HTTP_200_OK)

# New API for browse history
@api_view(['GET'])
def admin_browse_history(request):
    if not request.user.is_staff:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 10))
    
    from .models import BrowseHistory
    qs = BrowseHistory.objects.select_related('user', 'product').order_by('-viewed_at')
    
    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    items = qs[start:end]
    
    data = []
    for item in items:
        data.append({
            'id': item.id,
            'username': item.user.username if item.user else 'Anonymous',
            'product_name': item.product.name,
            'viewed_at': item.viewed_at
        })
        
    return Response({'total': total, 'results': data}, status=status.HTTP_200_OK)

# New API for User Profile
@api_view(['GET', 'POST'])
def user_profile(request):
    user = request.user
    if not user.is_authenticated:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
    if request.method == 'GET':
        from .models import Address, UserCoupon
        # Basic info
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'date_joined': user.date_joined,
            'is_staff': user.is_staff
        }
        
        # Address
        addr = Address.objects.filter(user=user).first()
        if addr:
            data['address'] = {
                'province': addr.province,
                'city': addr.city,
                'detail_address': addr.detail_address
            }
            
        # Coupons: Fetch from UserCoupon (only valid/unused ones or show status)
        # Requirement: "Delete used ones" -> show only unused
        ucs = UserCoupon.objects.filter(user=user, is_used=False).select_related('coupon').order_by('-assigned_at')
        today = timezone.localdate()
        coupons = []
        for uc in ucs:
            expiry_date = timezone.localtime(uc.coupon.valid_until).date()
            days_left = (expiry_date - today).days + 1
            if days_left < 0:
                days_left = 0
            coupons.append({
                'message': f"Coupon: {uc.coupon.code} - ${uc.coupon.discount_amount}",
                'date': uc.assigned_at,
                'code': uc.coupon.code,
                'discount': uc.coupon.discount_amount,
                'valid_until': uc.coupon.valid_until,
                'days_left': days_left
            })
        data['coupons'] = coupons
        
        return Response(data, status=status.HTTP_200_OK)
        
    elif request.method == 'POST':
        # Update info
        email = request.data.get('email')
        if email:
            user.email = email
            
        # Password change
        password = request.data.get('password')
        if password:
            user.set_password(password)
            
        user.save()
        
        # Address update
        from .models import Address
        province = request.data.get('province')
        city = request.data.get('city')
        detail_address = request.data.get('detail_address')
        
        # If any address field is provided, update or create
        if province or city or detail_address:
            addr, created = Address.objects.get_or_create(user=user)
            if province: addr.province = province
            if city: addr.city = city
            if detail_address: addr.detail_address = detail_address
            addr.save()
            
        return Response({'message': 'Profile updated'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def tags_list(request):
    from .models import Tag, ProductTag
    from .serializers import TagSerializer
    
    # Use our custom Tag model
    # Filter tags that are associated with at least one product
    tags = Tag.objects.filter(producttag__isnull=False).distinct().order_by('name')
    
    # Return objects using serializer
    return Response(TagSerializer(tags, many=True).data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_unread_count(request):
    user = request.user
    if not user.is_authenticated:
        return Response({'count': 0}, status=status.HTTP_200_OK)
        
    from .models import Message
    
    if user.is_staff:
        # Count unread messages from non-staff users
        count = Message.objects.filter(
            receiver__is_staff=True,
            is_read=False
        ).count()
    else:
        # Count unread messages sent to this user
        count = Message.objects.filter(
            receiver=user,
            is_read=False
        ).count()
        
    return Response({'count': count}, status=status.HTTP_200_OK)
