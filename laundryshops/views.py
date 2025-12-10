from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import LaundryService, ServiceType, ServiceOffering, OperatingHour, Review
from .serializers import (
    LaundryServiceSerializer, ServiceTypeSerializer, 
    ServiceOfferingSerializer, OperatingHourSerializer, ReviewSerializer
)

class IsVendor(permissions.BasePermission):
    """Permission class to check if user is a vendor"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.user_type == 'vendor'

class IsVendorOwner(permissions.BasePermission):
    """Permission class to check if user is the owner of the service"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.vendor == request.user

# Laundry Service Views
class LaundryServiceListCreateView(generics.ListCreateAPIView):
    queryset = LaundryService.objects.filter(is_active=True)
    serializer_class = LaundryServiceSerializer
    permission_classes = [IsVendor]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['shop_name', 'district', 'state', 'zipcode']
    ordering_fields = ['rating', 'shop_name', 'created_at']
    
    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)

class LaundryServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LaundryService.objects.all()
    serializer_class = LaundryServiceSerializer
    permission_classes = [IsVendorOwner]

class VendorServicesListView(generics.ListAPIView):
    """List all services owned by the authenticated vendor"""
    serializer_class = LaundryServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return LaundryService.objects.filter(vendor=self.request.user)

class LaundryServiceSearchView(generics.ListAPIView):
    serializer_class = LaundryServiceSerializer
    
    def get_queryset(self):
        queryset = LaundryService.objects.filter(is_active=True)
        query = self.request.query_params.get('q', '')
        district = self.request.query_params.get('district', '')
        state = self.request.query_params.get('state', '')
        zipcode = self.request.query_params.get('zipcode', '')
        city = self.request.query_params.get('city', '')
        
        if query:
            queryset = queryset.filter(
                Q(shop_name__icontains=query) |
                Q(description__icontains=query) |
                Q(address__icontains=query)
            )
        
        if district:
            queryset = queryset.filter(district__icontains=district)
        
        if state:
            queryset = queryset.filter(state__icontains=state)
        
        if zipcode:
            queryset = queryset.filter(zipcode__icontains=zipcode)
        
        if city:
            queryset = queryset.filter(
                Q(district__icontains=city) |
                Q(address__icontains=city)
            )
        
        return queryset

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def address_search(request):
    """
    Search for unique addresses, cities, states, and districts
    Query params: q (search term), type (address/city/state/district)
    """
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')
    
    if not query or len(query) < 2:
        return Response({
            'status': 'error',
            'message': 'Query must be at least 2 characters'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    results = {
        'districts': [],
        'states': [],
        'cities': [],
        'addresses': []
    }
    
    services = LaundryService.objects.filter(is_active=True)
    
    if search_type in ['all', 'district']:
        districts = services.filter(
            district__icontains=query
        ).values_list('district', flat=True).distinct()[:10]
        results['districts'] = list(districts)
    
    if search_type in ['all', 'state']:
        states = services.filter(
            state__icontains=query
        ).values_list('state', flat=True).distinct()[:10]
        results['states'] = list(states)
    
    if search_type in ['all', 'city']:
        cities = services.filter(
            Q(district__icontains=query)
        ).values_list('district', flat=True).distinct()[:10]
        results['cities'] = list(cities)
    
    if search_type in ['all', 'address']:
        addresses = services.filter(
            address__icontains=query
        ).values('address', 'district', 'state', 'zipcode').distinct()[:10]
        results['addresses'] = list(addresses)
    
    return Response({
        'status': 'success',
        'query': query,
        'results': results
    })

class LaundryServiceNearbyView(generics.ListAPIView):
    serializer_class = LaundryServiceSerializer
    
    def get_queryset(self):
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        radius = self.request.query_params.get('radius', 10)
        
        if not lat or not lng:
            return LaundryService.objects.none()
        
        try:
            lat = float(lat)
            lng = float(lng)
            radius = float(radius)
        except ValueError:
            return LaundryService.objects.none()
        
        # Simple distance calculation
        from math import radians, sin, cos, sqrt, atan2
        
        def calculate_distance(lat1, lon1, lat2, lon2):
            R = 6371
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            return R * c
        
        nearby_services = []
        for service in LaundryService.objects.filter(is_active=True):
            if service.latitude and service.longitude:
                distance = calculate_distance(lat, lng, float(service.latitude), float(service.longitude))
                if distance <= radius:
                    nearby_services.append(service.id)
        
        return LaundryService.objects.filter(id__in=nearby_services)

class AddReviewView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        laundry_service = get_object_or_404(LaundryService, id=self.kwargs['pk'])
        review = serializer.save(user=self.request.user, laundry_service=laundry_service)
        self.update_service_rating(laundry_service)
    
    def update_service_rating(self, laundry_service):
        reviews = laundry_service.reviews.all()
        if reviews.exists():
            total_rating = sum(review.rating for review in reviews)
            average_rating = total_rating / reviews.count()
            laundry_service.rating = round(average_rating, 2)
            laundry_service.total_reviews = reviews.count()
            laundry_service.save()

# Service Type Views
class ServiceTypeListCreateView(generics.ListCreateAPIView):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    permission_classes = [IsVendor]

class ServiceTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    permission_classes = [IsVendor]

# Service Offering Views
class ServiceOfferingListCreateView(generics.ListCreateAPIView):
    serializer_class = ServiceOfferingSerializer
    permission_classes = [IsVendor]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['service_type__name', 'laundry_service__shop_name']
    ordering_fields = ['price', 'service_type__name', 'laundry_service__shop_name']
    
    def get_queryset(self):
        # Vendors can only see offerings for their own services
        if self.request.user.is_authenticated and self.request.user.user_type == 'vendor':
            return ServiceOffering.objects.filter(laundry_service__vendor=self.request.user)
        return ServiceOffering.objects.all()


class ServiceOfferingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ServiceOfferingSerializer
    permission_classes = [IsVendor]
    
    def get_queryset(self):
        # Vendors can only access offerings for their own services
        if self.request.user.is_authenticated and self.request.user.user_type == 'vendor':
            return ServiceOffering.objects.filter(laundry_service__vendor=self.request.user)
        return ServiceOffering.objects.all()

# Operating Hour Views
class OperatingHourListCreateView(generics.ListCreateAPIView):
    serializer_class = OperatingHourSerializer
    permission_classes = [IsVendor]
    
    def get_queryset(self):
        # Vendors can only see operating hours for their own services
        if self.request.user.is_authenticated and self.request.user.user_type == 'vendor':
            return OperatingHour.objects.filter(laundry_service__vendor=self.request.user)
        return OperatingHour.objects.all()

class OperatingHourDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OperatingHourSerializer
    permission_classes = [IsVendor]
    
    def get_queryset(self):
        # Vendors can only access operating hours for their own services
        if self.request.user.is_authenticated and self.request.user.user_type == 'vendor':
            return OperatingHour.objects.filter(laundry_service__vendor=self.request.user)
        return OperatingHour.objects.all()

# Review Views
class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        laundry_service_id = self.kwargs.get('pk')
        if laundry_service_id:
            return Review.objects.filter(laundry_service_id=laundry_service_id)
        
        if self.request.user.is_authenticated:
            return Review.objects.filter(user=self.request.user)
        return Review.objects.all()
    
    def perform_create(self, serializer):
        laundry_service_id = self.request.data.get('laundry_service')
        if not laundry_service_id:
            laundry_service_id = self.kwargs.get('pk')
        
        laundry_service = get_object_or_404(LaundryService, id=laundry_service_id)
        serializer.save(user=self.request.user, laundry_service=laundry_service)
        self.update_service_rating(laundry_service)
    
    def update_service_rating(self, laundry_service):
        reviews = laundry_service.reviews.all()
        if reviews.exists():
            total_rating = sum(review.rating for review in reviews)
            average_rating = total_rating / reviews.count()
            laundry_service.rating = round(average_rating, 2)
            laundry_service.total_reviews = reviews.count()
            laundry_service.save()

class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Review.objects.filter(user=self.request.user)
        return Review.objects.all()
    
    def perform_update(self, serializer):
        review = self.get_object()
        serializer.save()
        self.update_service_rating(review.laundry_service)
    
    def perform_destroy(self, instance):
        laundry_service = instance.laundry_service
        instance.delete()
        self.update_service_rating(laundry_service)
    
    def update_service_rating(self, laundry_service):
        reviews = laundry_service.reviews.all()
        if reviews.exists():
            total_rating = sum(review.rating for review in reviews)
            average_rating = total_rating / reviews.count()
            laundry_service.rating = round(average_rating, 2)
            laundry_service.total_reviews = reviews.count()
            laundry_service.save()
        else:
            laundry_service.rating = 0.00
            laundry_service.total_reviews = 0
            laundry_service.save()