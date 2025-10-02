from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import User, UserProfile, OTP  # import OTP model


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'country_code', 'phone_number', 'is_staff', 'is_superuser', 'is_verified')
    list_filter = ('is_staff', 'is_superuser', 'is_verified')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Phone Info', {'fields': ('country_code', 'phone_number')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_verified')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'country_code', 'phone_number', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_verified'),
        }),
    )
    search_fields = ('email', 'phone_number')
    ordering = ('email',)
    filter_horizontal = ()


class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp_code', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__email', 'user__phone_number', 'otp_code')
    readonly_fields = ('created_at', 'expires_at')


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)
admin.site.register(OTP, OTPAdmin)
