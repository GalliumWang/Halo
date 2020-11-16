from django.urls import path
from .views import (
    ItemDetailView,
    CheckoutView,
    HomeView,
    OrderSummaryView,
    add_to_bookmark,
    remove_from_bookmark,
    remove_single_item_from_cart,
    PaymentView,
    AddCouponView,
    RequestRefundView,
    add_comment,
    remove_from_bookmark_sp,
    PeopleView,
    PeopleItemDetailView,
    follow_people,
    unfollow_people,
    follow_list,
    unfollow_people_sp,
    movie_year_view_1,  # data visualization
    relationship_view_people,  # data visualization
    relationship_view_movie  # data visualization
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('people', PeopleView.as_view(), name='people'),
    path('people/<slug>/', PeopleItemDetailView.as_view(), name='people-detail'),


    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('add-to-bookmark/<slug>/', add_to_bookmark, name='add-to-bookmark'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-bookmark/<slug>/',
         remove_from_bookmark, name='remove-from-bookmark'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
    path('movie/<slug>/', ItemDetailView.as_view(), name='movie'),
    path('add-comment/<slug>', add_comment, name='add-comment'),
    path('remove-from-bookmark-sp/<slug>/',
         remove_from_bookmark_sp, name='remove-from-bookmark-sp'),
    path('follow-people/<slug>/', follow_people, name='follow-people'),
    path('unfollow-people/<slug>/', unfollow_people, name='unfollow-people'),
    path('follow-list/', follow_list, name='follow-list'),

    path('unfollow-people-sp/<slug>/',
         unfollow_people_sp, name='unfollow-people-sp'),

    path('movie_year_view_1/', movie_year_view_1, name='movie_year_view_1'),

    path('relationship_view_people/<slug>', relationship_view_people,
         name='relationship_view_people'),

    path('relationship_view_movie/<slug>', relationship_view_movie,
         name='relationship_view_movie')





]
