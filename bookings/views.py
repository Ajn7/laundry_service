
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Booking, ServiceOffering
from .serializers import BookingSerializer

class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        service_offering_ids = self.request.data.get('service_offerings', [])
        service_offerings = ServiceOffering.objects.filter(id__in=service_offering_ids)
        
        total_price = sum(offering.price_per_unit for offering in service_offerings)
        
        serializer.save(
            user=self.request.user,
            total_price=total_price,
            service_offerings=service_offerings
        )

class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

class ShopBookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated] # Should be custom permission for shop owner

    def get_queryset(self):
        # This assumes the user is a shop owner and has a related laundry service
        # You'll need to implement the logic to get the laundry service for the current user
        laundry_service = self.request.user.laundryservice 
        return Booking.objects.filter(laundry_service=laundry_service)

class ShopBookingDetailView(generics.UpdateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated] # Should be custom permission for shop owner

    def get_queryset(self):
        laundry_service = self.request.user.laundryservice
        return Booking.objects.filter(laundry_service=laundry_service)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        new_status = request.data.get('status')
        if new_status:
            instance.status = new_status
            instance.save()
            return Response(self.get_serializer(instance).data)
        return Response({'error': 'Status not provided'}, status=status.HTTP_400_BAD_REQUEST)
