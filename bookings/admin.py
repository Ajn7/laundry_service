from django.contrib import admin
from .models import Booking

class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'laundry_service', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'laundry_service')
    search_fields = ('user__username', 'laundry_service__name')
    readonly_fields = ('created_at', 'updated_at', 'total_price', 'user', 'laundry_service', 'service_offerings')

admin.site.register(Booking, BookingAdmin)
