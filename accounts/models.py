from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import validate_email, RegexValidator
from django.core.exceptions import ValidationError
import uuid
import random
from django.utils import timezone
from datetime import timedelta


class UserManager(BaseUserManager):
    def _validate_input(self, email=None, country_code=None, phone_number=None):
        if not email and not (country_code and phone_number):
            raise ValueError('Either email or both country code and phone number must be set')

        if email:
            try:
                validate_email(email)
            except ValidationError:
                raise ValueError('Invalid email format')

        if country_code and not phone_number:
            raise ValueError('Phone number required when country code is provided')
        if phone_number and not country_code:
            raise ValueError('Country code required when phone number is provided')

    def create_user(self, email=None, country_code=None, phone_number=None, password=None, **extra_fields):
        self._validate_input(email, country_code, phone_number)

        email_norm = self.normalize_email(email) if email else None

        if email_norm and self.filter(email=email_norm).exists():
            raise ValueError('Email already exists')
        if phone_number and self.filter(country_code=country_code, phone_number=phone_number).exists():
            raise ValueError('Phone number already exists')

        user = self.model(
            email=email_norm,
            country_code=country_code,
            phone_number=phone_number,
            **extra_fields
        )

        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, country_code=None, phone_number=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)

        if not password:
            raise ValueError('Superusers must have a password')

        return self.create_user(email, country_code, phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    country_code = models.CharField(
        max_length=5, null=True, blank=True,
        validators=[RegexValidator(r'^\+\d{1,4}$', 'Country code must be in format +XXX')]
    )
    phone_number = models.CharField(
        max_length=15, null=True, blank=True,
        validators=[RegexValidator(r'^\d{6,15}$', 'Phone number must contain 6-15 digits')]
    )
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        if self.email:
            return self.email
        return self.full_phone or str(self.id)

    def generate_otp(self):
        """Generate OTP using the OTP model. Returns otp_code."""
        return OTP.generate_otp(self)

    def clean(self):
        if not self.email and not (self.country_code and self.phone_number):
            raise ValidationError('Either email or both country code and phone number must be provided')

        if self.email == "":
            self.email = None
        if self.country_code == "":
            self.country_code = None
        if self.phone_number == "":
            self.phone_number = None

    @property
    def full_phone(self):
        if self.country_code and self.phone_number:
            return f"{self.country_code}{self.phone_number}"
        return None


class OTP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.otp_code}"

    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()

    def mark_used(self):
        self.is_used = True
        self.save(update_fields=['is_used'])

    @classmethod
    def generate_otp(cls, user):
        # Invalidate previous unused OTPs (mark as used)
        cls.objects.filter(user=user, is_used=False).update(is_used=True)

        # Create new OTP
        otp_code = str(random.randint(100000, 999999)).zfill(6)
        expires_at = timezone.now() + timedelta(minutes=5)

        cls.objects.create(user=user, otp_code=otp_code, expires_at=expires_at)
        return otp_code


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.first_name or self.last_name:
            return f"{self.first_name or ''} {self.last_name or ''}".strip()
        return self.user.full_phone or str(self.user.id)

    @property
    def full_name(self):
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts)
