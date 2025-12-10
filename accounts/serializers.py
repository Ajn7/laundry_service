from rest_framework import serializers
from .models import User, UserProfile, OTP
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone
from rest_framework.authtoken.models import Token


class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    country_code = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=5,
        validators=[RegexValidator(r'^\+\d{1,4}$', 'Country code must be in format +XXX')]
    )
    phone_number = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=15,
        validators=[RegexValidator(r'^\d{6,15}$', 'Phone number must contain 6-15 digits')]
    )
    user_type = serializers.ChoiceField(
        choices=['customer', 'vendor'],
        default='customer',
        required=False
    )

    def validate(self, data):
        email = data.get('email')
        country_code = data.get('country_code')
        phone_number = data.get('phone_number')

        if not email and not (country_code and phone_number):
            raise serializers.ValidationError("Either email or both country code and phone number must be provided")

        if email:
            try:
                validate_email(email)
            except ValidationError:
                raise serializers.ValidationError("Invalid email format")

        if country_code and not phone_number:
            raise serializers.ValidationError("Phone number required when country code is provided")
        if phone_number and not country_code:
            raise serializers.ValidationError("Country code required when phone number is provided")

        return data


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    country_code = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    otp = serializers.CharField(max_length=6, write_only=True)
    user_type = serializers.ChoiceField(
        choices=['customer', 'vendor'],
        default='customer',
        required=False
    )

    def validate(self, data):
        email = data.get('email')
        country_code = data.get('country_code')
        phone_number = data.get('phone_number')
        otp_code = data.get('otp')
        user_type = data.get('user_type', 'customer')

        if not email and not (country_code and phone_number):
            raise serializers.ValidationError("Either email or both country code and phone number must be provided")

        # Find or create the user: SendOTP should have created it, but create here if not present
        if email:
            user, created = User.objects.get_or_create(email=email, defaults={'country_code': None, 'phone_number': None, 'user_type': user_type})
        else:
            user, created = User.objects.get_or_create(country_code=country_code, phone_number=phone_number, defaults={'email': None, 'user_type': user_type})

        # Lookup latest matching OTP for this user
        otp_qs = OTP.objects.filter(user=user, otp_code=otp_code, is_used=False, expires_at__gt=timezone.now())
        otp_obj = otp_qs.order_by('-created_at').first()
        if not otp_obj:
            raise serializers.ValidationError("Invalid or expired OTP")

        # Mark OTP used and verify user
        otp_obj.mark_used()
        user.is_verified = True
        user.save(update_fields=['is_verified'])

        data['user'] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'pincode', 'address']


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    full_phone = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'country_code', 'phone_number', 'full_phone', 'full_name', 'user_type', 'is_verified', 'profile', 'token']
        read_only_fields = ['is_verified', 'token', 'user_type']

    def get_profile(self, obj):
        try:
            return UserProfileSerializer(obj.profile).data
        except UserProfile.DoesNotExist:
            return None

    def get_full_phone(self, obj):
        return obj.full_phone

    def get_full_name(self, obj):
        try:
            return obj.profile.full_name
        except UserProfile.DoesNotExist:
            return ""

    def get_token(self, obj):
        token, _ = Token.objects.get_or_create(user=obj)
        return token.key
