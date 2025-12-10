from rest_framework import serializers
from .models import LaundryService, ServiceType, ServiceOffering, OperatingHour, Review
from django.contrib.auth.models import User

class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = '__all__'

class ServiceOfferingSerializer(serializers.ModelSerializer):
    service_type_name = serializers.CharField(source='service_type.name', read_only=True)
    
    class Meta:
        model = ServiceOffering
        fields = ['id', 'service_type', 'service_type_name', 'price', 'unit', 'estimated_time']

class OperatingHourSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = OperatingHour
        fields = ['id', 'day_of_week', 'day_name', 'opening_time', 'closing_time', 'is_closed']

class ReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    user_phone = serializers.ReadOnlyField(source='user.full_phone')
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'user_email', 'user_phone', 'customer_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']

class LaundryServiceSerializer(serializers.ModelSerializer):
    service_offerings = ServiceOfferingSerializer(many=True, required=False)
    operating_hours = OperatingHourSerializer(many=True, required=False)
    reviews = ReviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = LaundryService
        fields = [
            'id', 'vendor', 'shop_name', 'description', 'phone_number', 'email', 'website', 'locationUrl',
            'address', 'district', 'state', 'country', 'zipcode', 'latitude', 'longitude',
            'pickup_start_time', 'pickup_end_time', 'delivery_start_time', 'delivery_end_time',
            'rating', 'total_reviews', 'is_active', 'created_at', 'updated_at',
            'service_offerings', 'operating_hours', 'reviews'
        ]
        read_only_fields = ['vendor', 'rating', 'total_reviews', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        service_offerings_data = validated_data.pop('service_offerings', [])
        operating_hours_data = validated_data.pop('operating_hours', [])
        
        laundry_service = LaundryService.objects.create(**validated_data)
        
        # Create service offerings
        for offering_data in service_offerings_data:
            ServiceOffering.objects.create(laundry_service=laundry_service, **offering_data)
        
        # Create operating hours
        for hour_data in operating_hours_data:
            OperatingHour.objects.create(laundry_service=laundry_service, **hour_data)
        
        return laundry_service
    
    def update(self, instance, validated_data):
        service_offerings_data = validated_data.pop('service_offerings', None)
        operating_hours_data = validated_data.pop('operating_hours', None)
        
        # Update main fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update service offerings if provided
        if service_offerings_data is not None:
            # Delete existing offerings
            instance.service_offerings.all().delete()
            # Create new offerings
            for offering_data in service_offerings_data:
                ServiceOffering.objects.create(laundry_service=instance, **offering_data)
        
        # Update operating hours if provided
        if operating_hours_data is not None:
            # Delete existing hours
            instance.operating_hours.all().delete()
            # Create new hours
            for hour_data in operating_hours_data:
                OperatingHour.objects.create(laundry_service=instance, **hour_data)
        
        return instance