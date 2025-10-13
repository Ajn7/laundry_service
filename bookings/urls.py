
from django.urls import path
from .views import (
    BookingListCreateView,
    BookingDetailView,
    ShopBookingListView,
    ShopBookingDetailView,
)

urlpatterns = [
    path('bookings/', BookingListCreateView.as_view(), name='booking_list_create'),
    path('bookings/<int:pk>/', BookingDetailView.as_view(), name='booking_detail'),
    path('shop/bookings/', ShopBookingListView.as_view(), name='shop_booking_list'),
    path('shop/bookings/<int:pk>/', ShopBookingDetailView.as_view(), name='shop_booking_detail'),
]
