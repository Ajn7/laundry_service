from django.urls import path
from .views import (
    LaundryServiceListCreateView,
    LaundryServiceDetailView,
    ServiceTypeListCreateView,
    ServiceTypeDetailView,
    ServiceOfferingListCreateView,
    ServiceOfferingDetailView,
    OperatingHourListCreateView,
    OperatingHourDetailView,
    ReviewListCreateView,
    ReviewDetailView,
    LaundryServiceSearchView,
    LaundryServiceNearbyView,
    AddReviewView,
    VendorServicesListView,
    address_search
)

urlpatterns = [
    # Laundry Service endpoints
    path('services/', LaundryServiceListCreateView.as_view(), name='service_list_create'),
    path('services/<int:pk>/', LaundryServiceDetailView.as_view(), name='service_detail'),
    path('services/search/', LaundryServiceSearchView.as_view(), name='service_search'),
    path('services/nearby/', LaundryServiceNearbyView.as_view(), name='service_nearby'),
    path('services/<int:pk>/add-review/', AddReviewView.as_view(), name='add_review'),
    path('services/<int:pk>/reviews/', ReviewListCreateView.as_view(), name='service_reviews'),
    
    # Vendor specific endpoints
    path('vendor/services/', VendorServicesListView.as_view(), name='vendor_services_list'),
    
    # Address search endpoint
    path('address-search/', address_search, name='address_search'),
    
    # Service Type endpoints
    path('service-types/', ServiceTypeListCreateView.as_view(), name='service_type_list_create'),
    path('service-types/<int:pk>/', ServiceTypeDetailView.as_view(), name='service_type_detail'),
    
    # Service Offering endpoints
    path('service-offerings/', ServiceOfferingListCreateView.as_view(), name='service_offering_list_create'),
    path('service-offerings/<int:pk>/', ServiceOfferingDetailView.as_view(), name='service_offering_detail'),
    
    # Operating Hour endpoints
    path('operating-hours/', OperatingHourListCreateView.as_view(), name='operating_hour_list_create'),
    path('operating-hours/<int:pk>/', OperatingHourDetailView.as_view(), name='operating_hour_detail'),
    
    # Review endpoints
    path('reviews/', ReviewListCreateView.as_view(), name='review_list_create'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review_detail'),
]