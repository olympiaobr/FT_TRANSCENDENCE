import logging
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.shortcuts import render, redirect
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Profile, TwoFactorCode
from .serializers import UserSerializer, ProfileSerializer
from django.middleware.csrf import get_token
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from django.core.mail import send_mail


logger = logging.getLogger('django')


def create_tokens(user, two_fa_status=False):
    """
    Generate JWT tokens with 2FA status claim.
    """
    refresh = RefreshToken.for_user(user)
    refresh['2fa_status'] = two_fa_status
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def sanitize_response(data, keys_to_exclude=None):
    """
    Remove sensitive data like `password` from responses.
    """
    if keys_to_exclude is None:
        keys_to_exclude = ["password"]
    if isinstance(data, list):
        for item in data:
            for key in keys_to_exclude:
                item.pop(key, None)
    elif isinstance(data, dict):
        for key in keys_to_exclude:
            data.pop(key, None)
    return data

def send_email_code(user, otp_code):
    subject = "Your OTP Code"
    message = f"Hello {user.username},\n\nYour OTP code is {otp_code}. It is valid for 5 minutes."
    send_mail(subject, message, "no-reply@example.com", [user.email])

def generate_otp(user):
    otp, _ = TwoFactorCode.objects.get_or_create(user=user)
    otp.code = get_random_string(length=6, allowed_chars='0123456789')
    otp.timestamp = now()
    otp.save()
    logger.info(f"Generated OTP for {user.username}: {otp.code}")
    send_email_code(user, otp.code)

@api_view(['POST'])
def signup_view(request):
    logger.info("Signup request received.")
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if not username or not password or not email:
        logger.error("Invalid signup data.")
        return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        logger.error(f"Username already exists: {username}")
        return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.create_user(username=username, password=password, email=email)
        logger.info(f"User created: {username} (ID: {user.id})")
        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
    except IntegrityError as e:
        logger.error(f"IntegrityError during signup: {e}")
        return Response({"error": "An error occurred during signup."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def login_view(request):

    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)

    if user:
        if user.profile.twoFA_active:
            generate_otp(user)
            return Response({
                "message": "2FA required. OTP sent to your email.",
                "two_fa_required": True,
                "username": user.username
            }, status=status.HTTP_200_OK)

        tokens = create_tokens(user, two_fa_status=True)
        login(request, user)
        return Response({
            "message": "Login successful.",
            "tokens": tokens
        }, status=status.HTTP_200_OK)

    return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@login_required
def resend_otp(request):
    user = request.user
    otp_record = TwoFactorCode.objects.filter(user=user).first()
    if otp_record and (now() - otp_record.timestamp).seconds < 30:
        return Response({"error": "Please wait before requesting another OTP."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    generate_otp(user)
    return Response({"message": "New OTP sent to your email."}, status=status.HTTP_200_OK)

@api_view(['POST'])
@login_required
def verify_2fa(request):
    otp_code = request.data.get('otp')
    attempts_key = f"otp_attempts_{request.user.id}"
    attempts = cache.get(attempts_key, 0)

    if attempts >= 5:
        return Response({"error": "Too many attempts. Please try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    try:
        otp = TwoFactorCode.objects.get(user=request.user, code=otp_code)
        if otp.is_valid():
            otp.delete()
            cache.delete(attempts_key)
            refresh = RefreshToken.for_user(request.user)
            refresh['2fa_complete'] = True
            return Response({
                "message": "2FA verification successful.",
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }, status=status.HTTP_200_OK)
        cache.incr(attempts_key)
        cache.expire(attempts_key, 300)
        return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
    except TwoFactorCode.DoesNotExist:
        cache.incr(attempts_key)
        cache.expire(attempts_key, 300)
        return Response({"error": "Invalid OTP."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@login_required
def toggle_2fa(request):
    enable = request.data.get('enable', False)
    profile = request.user.profile

    if enable:
        generate_otp(request.user)
        profile.twoFA_active = True
        profile.save()
        return Response({"message": "2FA enabled. OTP sent to your email."}, status=status.HTTP_200_OK)
    else:
        profile.twoFA_active = False
        TwoFactorCode.objects.filter(user=request.user).delete()
        profile.save()
        return Response({"message": "2FA disabled."}, status=status.HTTP_200_OK)

@api_view(['POST'])
def logout_view(request):
    tokens = OutstandingToken.objects.filter(user=request.user)
    for token in tokens:
        token.blacklist()
    logout(request)
    return Response({"message": "Logged out and tokens blacklisted successfully"}, status=status.HTTP_200_OK)

@api_view(['GET'])
def profile_view(request):
    if not request.user.is_authenticated:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)
        data = serializer.data
        data['csrf_token'] = get_token(request)
        return Response(data, status=status.HTTP_200_OK)
    except Profile.DoesNotExist:
        return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@login_required
@parser_classes([MultiPartParser, FormParser])
def update_profile_view(request):
    profile = Profile.objects.get(user=request.user)
    serializer = ProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        user = profile.user
        email = request.data.get('email')
        if email:
            user.email = email
            user.save()

        serializer.save()
        return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@login_required
@parser_classes([MultiPartParser, FormParser])
def upload_avatar(request):
    profile = Profile.objects.get(user=request.user)
    file = request.FILES.get('avatar')
    if file:
        profile.avatar.save(file.name, file, save=True)
        return Response({'message': 'Avatar updated successfully'}, status=status.HTTP_200_OK)
    return Response({'error': 'No avatar provided'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@login_required
def add_friend_view(request):
    friend_username = request.data.get('friend_username')
    try:
        friend = User.objects.get(username=friend_username)
        profile = request.user.profile
        if friend.profile not in profile.friends.all():
            profile.friends.add(friend.profile)
            return Response({"message": "Friend added successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Already friends"}, status=status.HTTP_409_CONFLICT)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
