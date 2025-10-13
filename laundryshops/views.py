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

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser

# Laundry Service Views
class LaundryServiceListCreateView(generics.ListCreateAPIView):
    queryset = LaundryService.objects.filter(is_active=True)
    serializer_class = LaundryServiceSerializer
    permission_classes = [IsSuperAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['shop_name', 'district', 'state', 'zipcode']
    ordering_fields = ['rating', 'shop_name', 'created_at']

class LaundryServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LaundryService.objects.all()
    serializer_class = LaundryServiceSerializer
    permission_classes = [IsSuperAdmin]

class LaundryServiceSearchView(generics.ListAPIView):
    serializer_class = LaundryServiceSerializer
    
    def get_queryset(self):
        queryset = LaundryService.objects.filter(is_active=True)
        query = self.request.query_params.get('q', '')
        district = self.request.query_params.get('district', '')
        state = self.request.query_params.get('state', '')
        zipcode = self.request.query_params.get('zipcode', '')
        
        if query:
            queryset = queryset.filter(
                Q(shop_name__icontains=query) |
                Q(description__icontains=query)
            )
        
        if district:
            queryset = queryset.filter(district__icontains=district)
        
        if state:
            queryset = queryset.filter(state__icontains=state)
        
        if zipcode:
            queryset = queryset.filter(zipcode__icontains=zipcode)
        
        return queryset

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
    permission_classes = [IsSuperAdmin]

class ServiceTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    permission_classes = [IsSuperAdmin]

# Service Offering Views
class ServiceOfferingListCreateView(generics.ListCreateAPIView):
    queryset = ServiceOffering.objects.all()
    serializer_class = ServiceOfferingSerializer
    permission_classes = [IsSuperAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['service_type__name', 'laundry_service__shop_name']
    ordering_fields = ['price', 'service_type__name', 'laundry_service__shop_name']


class ServiceOfferingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceOffering.objects.all()
    serializer_class = ServiceOfferingSerializer
    permission_classes = [IsSuperAdmin]

# Operating Hour Views
class OperatingHourListCreateView(generics.ListCreateAPIView):
    queryset = OperatingHour.objects.all()
    serializer_class = OperatingHourSerializer
    permission_classes = [IsSuperAdmin]

class OperatingHourDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OperatingHour.objects.all()
    serializer_class = OperatingHourSerializer
    permission_classes = [IsSuperAdmin]

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