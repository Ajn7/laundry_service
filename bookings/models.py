
from django.db import models
from django.conf import settings
from laundryshops.models import LaundryService, ServiceOffering

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    laundry_service = models.ForeignKey(LaundryService, on_delete=models.CASCADE, related_name='bookings')
    service_offerings = models.ManyToManyField(ServiceOffering)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        user_identifier = self.user.email or self.user.full_phone or str(self.user.id)
        return f"Booking {self.id} by {user_identifier}"
