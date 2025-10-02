from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class LaundryService(models.Model):
    """Main model for laundry service providers"""
    
    # Basic information
    shop_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    
    # Contact information
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    locationUrl=models.URLField(blank=True,null=True)
    
    # Location information
    address = models.TextField(blank=True,null=True)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="India")
    zipcode= models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    #location = gis_models.PointField(blank=True, null=True, srid=4326)
    
    # Timing information
    pickup_start_time = models.TimeField()
    pickup_end_time = models.TimeField()
    delivery_start_time = models.TimeField()
    delivery_end_time = models.TimeField()
    
    # Ratings
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(5.00)]
    )
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-rating', 'shop_name']
    
    def __str__(self):
        return self.shop_name


class ServiceType(models.Model):
    """Model for different types of laundry services"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name


class ServiceOffering(models.Model):
    """Model to track which services a laundry shop offers"""
    
    laundry_service = models.ForeignKey(
        LaundryService, 
        on_delete=models.CASCADE, 
        related_name='service_offerings'
    )
    service_type = models.ForeignKey(
        ServiceType, 
        on_delete=models.CASCADE,
        related_name='service_offerings'
    )
    price = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=50, default="per item")  # per item, per kg, etc.
    estimated_time = models.DurationField(blank=True, null=True)  # Estimated time to complete
    
    class Meta:
        unique_together = ['laundry_service', 'service_type']
    
    def __str__(self):
        return f"{self.laundry_service.shop_name} - {self.service_type.name}"


class OperatingHour(models.Model):
    """Model for shop operating hours"""
    
    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, _('Monday')
        TUESDAY = 1, _('Tuesday')
        WEDNESDAY = 2, _('Wednesday')
        THURSDAY = 3, _('Thursday')
        FRIDAY = 4, _('Friday')
        SATURDAY = 5, _('Saturday')
        SUNDAY = 6, _('Sunday')
    
    laundry_service = models.ForeignKey(
        LaundryService, 
        on_delete=models.CASCADE, 
        related_name='operating_hours'
    )
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_closed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['laundry_service', 'day_of_week']
        ordering = ['day_of_week', 'opening_time']
    
    def __str__(self):
        return f"{self.laundry_service.shop_name} - {self.get_day_of_week_display()}"


class Review(models.Model):
    """Model for customer reviews"""
    
    laundry_service = models.ForeignKey(
        LaundryService, 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    customer_name = models.CharField(max_length=255)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer_name} - {self.laundry_service.shop_name} - {self.rating}"