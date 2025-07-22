from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from .models import User, VerificationCode, PasswordResetRequest
from django.shortcuts import get_object_or_404
import random
import jwt
from django.conf import settings
import os
import requests

ESKIZ_EMAIL = os.environ.get('ESKIZ_EMAIL')
ESKIZ_PASSWORD = os.environ.get('ESKIZ_PASSWORD')
ESKIZ_BASE_URL = 'https://notify.eskiz.uz/api/'

_eskiz_token = None

def get_eskiz_token():
    global _eskiz_token
    if _eskiz_token:
        return _eskiz_token
    resp = requests.post(
        ESKIZ_BASE_URL + 'auth/login',
        data={'email': ESKIZ_EMAIL, 'password': ESKIZ_PASSWORD}
    )
    resp.raise_for_status()
    _eskiz_token = resp.json()['data']['token']
    return _eskiz_token

def send_sms_via_eskiz(phone, message):
    token = get_eskiz_token()
    headers = {'Authorization': f'Bearer {token}'}
    data = {'mobile_phone': phone, 'message': message, 'from': '4546'}
    resp = requests.post(ESKIZ_BASE_URL + 'message/sms/send', headers=headers, data=data)
    resp.raise_for_status()
    return resp.json()

class RegisterSMSSendCode(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        if not phone:
            return Response({'error': 'Phone required'}, status=status.HTTP_400_BAD_REQUEST)
        code = str(random.randint(100000, 999999))
        user, _ = User.objects.get_or_create(phone=phone, username=phone)
        VerificationCode.objects.create(user=user, code=code, purpose='register')
        send_sms_via_eskiz(phone, f'Your verification code: {code}')
        return Response({'message': 'Code sent'})

class Register(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        code = request.data.get('code')
        password = request.data.get('password')
        user = get_object_or_404(User, phone=phone)
        v = VerificationCode.objects.filter(user=user, code=code, purpose='register').order_by('-created_at').first()
        if not v or (timezone.now() - v.created_at).seconds > 600:
            return Response({'error': 'Invalid or expired code'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password)
        user.is_phone_verified = True
        user.save()
        return Response({'message': 'Registered'})

class Login(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')
        user = authenticate(username=phone, password=password)
        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        payload = {'user_id': user.id, 'exp': timezone.now() + timezone.timedelta(hours=1)}
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return Response({'token': token})

class RefreshToken(APIView):
    def post(self, request):
        token = request.data.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            new_payload = {'user_id': user.id, 'exp': timezone.now() + timezone.timedelta(hours=1)}
            new_token = jwt.encode(new_payload, settings.SECRET_KEY, algorithm='HS256')
            return Response({'token': new_token})
        except Exception:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

class ParolniTiklash(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        code = str(random.randint(100000, 999999))
        user = get_object_or_404(User, phone=phone)
        PasswordResetRequest.objects.create(user=user, code=code)
        send_sms_via_eskiz(phone, f'Your password reset code: {code}')
        return Response({'message': 'Reset code sent'})

class UsernamePasswordResetSMS(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        code = request.data.get('code')
        new_password = request.data.get('new_password')
        user = get_object_or_404(User, phone=phone)
        reset = PasswordResetRequest.objects.filter(user=user, code=code, is_used=False).order_by('-created_at').first()
        if not reset or (timezone.now() - reset.created_at).seconds > 600:
            return Response({'error': 'Invalid or expired code'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        reset.is_used = True
        reset.save()
        return Response({'message': 'Password reset successful'})
