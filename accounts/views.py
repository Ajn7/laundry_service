from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.db import transaction
from rest_framework.permissions import AllowAny
from .models import User, UserProfile, OTP
from .serializers import (
    SendOTPSerializer,
    VerifyOTPSerializer,
    UserProfileSerializer,
    UserSerializer,
)
from rest_framework.authtoken.models import Token


class SendOTPView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            country_code = serializer.validated_data.get('country_code')
            phone_number = serializer.validated_data.get('phone_number')

            try:
                # Create or get the user record (minimal user). This keeps the flow idempotent.
                if email:
                    user, created = User.objects.get_or_create(
                        email=email,
                        defaults={'country_code': None, 'phone_number': None}
                    )
                else:
                    user, created = User.objects.get_or_create(
                        country_code=country_code,
                        phone_number=phone_number,
                        defaults={'email': None}
                    )
            except Exception as e:
                return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            # Generate OTP using the OTP model
            otp_code = user.generate_otp()

            # TODO: Integrate with your SMS/email service here
            # send_otp_via_sms(user.full_phone, otp_code)
            # send_otp_via_email(user.email, otp_code)

            response_data = {'status': 'success', 'message': 'OTP sent successfully'}
            if settings.DEBUG:
                response_data['otp'] = otp_code

            return Response(response_data, status=status.HTTP_200_OK)

        return Response({'status': 'error', 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Get or create token
            token, _ = Token.objects.get_or_create(user=user)

            # Prepare response payload
            profile = getattr(user, 'profile', None)
            full_name = profile.full_name if profile else None
            response_data = {
                'status': 'success',
                'user_exists': bool(profile),
                'user_id': user.id,
                'full_name': full_name,
                'token': token.key,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        return Response({'status': 'error', 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get user profile with complete user data"""
        user_serializer = UserSerializer(request.user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create user profile"""
        if hasattr(request.user, 'profile'):
            return Response({'status': 'error', 'message': 'Profile already exists'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            user_serializer = UserSerializer(request.user)
            return Response({'status': 'success', 'message': 'Profile created successfully', 'user': user_serializer.data}, status=status.HTTP_201_CREATED)

        return Response({'status': 'error', 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """Full update of user profile"""
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response({'status': 'error', 'message': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            user_serializer = UserSerializer(request.user)
            return Response({'status': 'success', 'message': 'Profile updated successfully', 'user': user_serializer.data}, status=status.HTTP_200_OK)

        return Response({'status': 'error', 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """Partial update of user profile"""
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response({'status': 'error', 'message': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            user_serializer = UserSerializer(request.user)
            return Response({'status': 'success', 'message': 'Profile updated successfully', 'user': user_serializer.data}, status=status.HTTP_200_OK)

        return Response({'status': 'error', 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
