fffrom django.contrib import admin
from .models import LaundryService, ServiceType, ServiceOffering, OperatingHour, Review


@admin.register(LaundryService)
class LaundryServiceAdmin(admin.ModelAdmin):
    list_display = ('shop_name', 'district', 'state', 'country', 'is_active', 'rating', 'total_reviews')
    search_fields = ('shop_name', 'district', 'state', 'country')
    list_filter = ('is_active', 'district', 'state', 'country')
    ordering = ('shop_name',)


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(ServiceOffering)
class ServiceOfferingAdmin(admin.ModelAdmin):
    list_display = ('laundry_service', 'service_type', 'price', 'unit', 'estimated_time')
    list_filter = ('laundry_service', 'service_type')
    search_fields = ('laundry_service__shop_name', 'service_type__name')


@admin.register(OperatingHour)
class OperatingHourAdmin(admin.ModelAdmin):
    list_display = ('laundry_service', 'day_of_week', 'opening_time', 'closing_time', 'is_closed')
    list_filter = ('day_of_week', 'is_closed')
    search_fields = ('laundry_service__shop_name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'laundry_service', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('customer_name', 'laundry_service__shop_name')
