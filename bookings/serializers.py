
from rest_framework import serializers
from .models import Booking
from laundryshops.serializers import ServiceOfferingSerializer

class BookingSerializer(serializers.ModelSerializer):
    service_offerings = ServiceOfferingSerializer(many=True, read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('user', 'total_price',)
