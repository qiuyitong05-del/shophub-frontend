"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from shop_app.views import (
    register_user,
    login_user,
    admin_login_user,
    category_list,
    product_list,
    product_detail,
    add_to_cart,
    get_cart,
    update_cart_item,
    remove_from_cart,
    checkout,
    orders_list,
    order_detail,
    cancel_order,
    admin_products,
    admin_product_detail,
    admin_create_product,
    admin_update_product,
    admin_disable_product,
    admin_enable_product,
    admin_orders,
    admin_order_detail,
    admin_add_product_photo,
    admin_remove_product_photo,
    update_order_status,
    admin_ship_order,
    admin_hold_order,
    default_address,
    upload_image,
    tags_list,
    create_review,
    create_long_term_review,
    edit_long_term_review,
    product_reviews,
    admin_all_reviews,
    admin_reply_review,
    edit_review,
    delete_review,
    add_review_followup,
    vote_review,
    product_questions,
    create_question,
    create_answer,
    delete_question,
    delete_answer,
    get_notifications,
    mark_notification_read,
    get_wishlist,
    add_to_wishlist,
    remove_from_wishlist,
    update_wishlist_privacy,
    wishlist_bulk_add_to_cart,
    admin_search_analytics,
    admin_wishlist_analytics,
    admin_issue_wishlist_coupon,
    get_notification_settings,
    update_notification_settings,
    get_messages,
    send_message,
    get_unread_count,
    admin_chat_conversations,
    user_profile,
    admin_browse_history,
    get_available_coupons,
    move_to_wishlist,
    get_cart_recommendations,
    find_similar_products,
    get_user_product_review_eligibility,
    edit_answer
)

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', register_user, name='register'),
    path('api/login/', login_user, name='login'),
    path('api/admin/login/', admin_login_user, name='admin_login'),
    path('api/categories/', category_list, name='category_list'),
    path('api/products/', product_list, name='product_list'),
    path('api/products/<int:pk>/', product_detail, name='product_detail'),
    path('api/products/<int:product_id>/eligibility/', get_user_product_review_eligibility, name='get_user_product_review_eligibility'),
    path('api/cart/add/', add_to_cart, name='add_to_cart'),
    path('api/cart/', get_cart, name='get_cart'),
    path('api/cart/update/', update_cart_item, name='update_cart_item'),
    path('api/cart/remove/', remove_from_cart, name='remove_from_cart'),
    path('api/checkout/', checkout, name='checkout'),
    
    # New Cart/Wishlist Features
    path('api/coupons/available/', get_available_coupons, name='get_available_coupons'),
    path('api/cart/move-to-wishlist/', move_to_wishlist, name='move_to_wishlist'),
    path('api/cart/recommendations/', get_cart_recommendations, name='get_cart_recommendations'),
    path('api/products/<int:product_id>/similar/', find_similar_products, name='find_similar_products'),

    path('api/orders/', orders_list, name='orders_list'),
    path('api/orders/<int:order_id>/', order_detail, name='order_detail'),
    path('api/orders/<int:order_id>/cancel/', cancel_order, name='cancel_order'),
    path('api/user/address/default/', default_address, name='default_address_v1'), # Keep for backward compatibility if any
    path('api/address/default/', default_address, name='default_address'), # Fix for frontend
    path('api/notifications/', get_notifications, name='get_notifications'),
    path('api/notifications/<int:notification_id>/read/', mark_notification_read, name='mark_notification_read'),
    
    # Wishlist
    path('api/wishlist/', get_wishlist, name='get_wishlist'),
    path('api/wishlist/add/', add_to_wishlist, name='add_to_wishlist'),
    path('api/wishlist/remove/', remove_from_wishlist, name='remove_from_wishlist'),
    path('api/wishlist/privacy/', update_wishlist_privacy, name='update_wishlist_privacy'),
    path('api/wishlist/bulk-cart/', wishlist_bulk_add_to_cart, name='wishlist_bulk_add_to_cart'),

    # Admin Analytics
    path('api/admin/analytics/search/', admin_search_analytics, name='admin_search_analytics'),
    path('api/admin/analytics/wishlist/', admin_wishlist_analytics, name='admin_wishlist_analytics'),
    path('api/admin/marketing/wishlist-coupon/', admin_issue_wishlist_coupon, name='admin_issue_wishlist_coupon'),

    # Admin
    path('api/admin/products/', admin_products, name='admin_products'),
    path('api/admin/products/<int:product_id>/', admin_product_detail, name='admin_product_detail'),
    path('api/admin/products/create/', admin_create_product, name='admin_create_product'),
    path('api/admin/products/<int:product_id>/update/', admin_update_product, name='admin_update_product'),
    path('api/admin/products/<int:product_id>/disable/', admin_disable_product, name='admin_disable_product'),
    path('api/admin/products/<int:product_id>/enable/', admin_enable_product, name='admin_enable_product'),
    path('api/admin/orders/', admin_orders, name='admin_orders'),
    path('api/admin/orders/<int:order_id>/', admin_order_detail, name='admin_order_detail'),
    path('api/admin/products/<int:product_id>/photos/add/', admin_add_product_photo, name='admin_add_product_photo'),
    path('api/admin/products/<int:product_id>/photos/<int:photo_id>/remove/', admin_remove_product_photo, name='admin_remove_product_photo'),
    path('api/admin/orders/<int:order_id>/status/', update_order_status, name='update_order_status'),
    path('api/admin/orders/<int:order_id>/ship/', admin_ship_order, name='admin_ship_order'),
    path('api/admin/orders/<int:order_id>/hold/', admin_hold_order, name='admin_hold_order'),

    # Tags
    path('api/tags/', tags_list, name='tags_list'),
    
    # Upload
    path('api/upload/', upload_image, name='upload_image'),
    
    # Reviews (Enhanced)
    path('api/reviews/create/', create_review, name='create_review'),
    path('api/reviews/long-term/create/', create_long_term_review, name='create_long_term_review'), # X13
    path('api/reviews/long-term/<int:review_id>/edit/', edit_long_term_review, name='edit_long_term_review'), # New: Edit long-term review
    path('api/products/<int:product_id>/reviews/', product_reviews, name='product_reviews'),
    path('api/reviews/<int:review_id>/edit/', edit_review, name='edit_review'),
    path('api/reviews/<int:review_id>/delete/', delete_review, name='delete_review'),
    path('api/reviews/<int:review_id>/followup/', add_review_followup, name='add_review_followup'),
    path('api/reviews/<int:review_id>/vote/', vote_review, name='vote_review'),
    
    # Admin Reviews
    path('api/admin/reviews/', admin_all_reviews, name='admin_all_reviews'),
    path('api/admin/reviews/<int:review_id>/reply/', admin_reply_review, name='admin_reply_review'),
    
    # Q&A
    path('api/products/<int:product_id>/questions/', product_questions, name='product_questions'),
    path('api/questions/create/', create_question, name='create_question'),
    path('api/questions/<int:question_id>/answer/', create_answer, name='create_answer'),
    path('api/questions/<int:question_id>/delete/', delete_question, name='delete_question'),
    path('api/answers/<int:answer_id>/delete/', delete_answer, name='delete_answer'),
    path('api/answers/<int:answer_id>/edit/', edit_answer, name='edit_answer'), # New

    # Notification Settings (X2)
    path('api/settings/notifications/', get_notification_settings, name='get_notification_settings'),
    path('api/settings/notifications/update/', update_notification_settings, name='update_notification_settings'),
    
    # Private Chat (X10)
    path('api/chat/messages/', get_messages, name='get_messages'),
    path('api/chat/send/', send_message, name='send_message'),
    path('api/chat/unread/', get_unread_count, name='get_unread_count'),
    path('api/admin/chat/conversations/', admin_chat_conversations, name='admin_chat_conversations'),
    
    # User Profile (New)
    path('api/user/profile/', user_profile, name='user_profile'),
    
    # Admin Browse History (New)
    path('api/admin/analytics/browse/', admin_browse_history, name='admin_browse_history'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
