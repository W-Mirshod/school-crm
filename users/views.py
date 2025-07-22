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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import string
from django.utils.crypto import get_random_string
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
load_dotenv()

ESKIZ_EMAIL = os.environ.get("ESKIZ_EMAIL")
ESKIZ_PASSWORD = os.environ.get("ESKIZ_PASSWORD")
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

def send_sms_via_eskiz(phone, message, code=None):
    # Ensure phone is in correct format
    if phone.isdigit() and len(phone) == 9:
        phone = '998' + phone
    token = get_eskiz_token()
    headers = {'Authorization': f'Bearer {token}'}
    data = {'mobile_phone': phone, 'message': message, 'from': '4546'}
    try:
        resp = requests.post(ESKIZ_BASE_URL + 'message/sms/send', headers=headers, data=data)
        print('Eskiz response:', resp.status_code, resp.text)
        resp.raise_for_status()
        return resp.json()
    except requests.HTTPError as e:
        print('Eskiz error response:', resp.status_code, resp.text)
        # If in test mode, retry with allowed test message
        if resp.status_code == 400 and any(t in message for t in ['Your verification code', 'code']):
            test_message = 'This is test from Eskiz'
            data['message'] = test_message
            resp = requests.post(ESKIZ_BASE_URL + 'message/sms/send', headers=headers, data=data)
            print('Eskiz test mode response:', resp.status_code, resp.text)
            resp.raise_for_status()
            return resp.json()
        raise

@method_decorator(csrf_exempt, name='dispatch')
class RegisterSMSSendCode(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'phone': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['phone']
        ),
        responses={200: openapi.Response('Code sent', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'message': openapi.Schema(type=openapi.TYPE_STRING)})),
                   400: 'Phone required'}
    )
    def post(self, request):
        phone = request.data.get('phone')
        if not phone:
            return Response({'error': 'Phone required'}, status=status.HTTP_400_BAD_REQUEST)
        code = str(random.randint(100000, 999999))
        user, _ = User.objects.get_or_create(phone=phone, username=phone)
        VerificationCode.objects.create(user=user, code=code, purpose='register')
        try:
            send_sms_via_eskiz(phone, f'aqillimaktab.uz sayti uchun hisobni tasdiqlash kodi: {code}', code=code)
            return Response({'message': 'Code sent'})
        except requests.HTTPError as e:
            # Only expose code if error is due to test mode or message restriction
            try:
                error_json = e.response.json()
                error_text = str(error_json)
            except Exception:
                error_text = e.response.text if hasattr(e.response, 'text') else str(e)
            if 'test' in error_text.lower() or 'allowed' in error_text.lower() or 'message' in error_text.lower():
                return Response({'message': 'Test mode: code sent', 'code': code})
            return Response({'error': 'Failed to send SMS. Please try again later.'}, status=500)

class Register(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                'code': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                'full_name': openapi.Schema(type=openapi.TYPE_STRING),
                'school_name': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['phone', 'code', 'password', 'full_name', 'school_name']
        ),
        responses={200: openapi.Response('Registered', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'message': openapi.Schema(type=openapi.TYPE_STRING)})),
                   400: 'Invalid or expired code'}
    )
    def post(self, request):
        phone = request.data.get('phone')
        code = request.data.get('code')
        password = request.data.get('password')
        full_name = request.data.get('full_name')
        school_name = request.data.get('school_name')
        user = get_object_or_404(User, phone=phone)
        v = VerificationCode.objects.filter(user=user, code=code, purpose='register').order_by('-created_at').first()
        if not v or (timezone.now() - v.created_at).seconds > 600:
            return Response({'error': 'Invalid or expired code'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password)
        user.is_phone_verified = True
        # Save full_name to first_name/last_name
        if full_name:
            parts = full_name.strip().split()
            user.first_name = parts[0]
            user.last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
        user.save()
        # Use full_name for SMS login, fallback to username
        login_name = full_name if full_name else user.username
        try:
            send_sms_via_eskiz(phone, f"Siz aqillimaktab.uz  platformasidan muvaffaqiyatli ro'yxatdan o'tdingiz.\nLogin: {login_name}\nParol: {password}")
        except Exception:
            pass
        return Response({'message': 'Registered'})

class Login(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['phone', 'password']
        ),
        responses={200: openapi.Response('Token', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'token': openapi.Schema(type=openapi.TYPE_STRING)})),
                   401: 'Invalid credentials'}
    )
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
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['token']
        ),
        responses={200: openapi.Response('Token', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'token': openapi.Schema(type=openapi.TYPE_STRING)})),
                   400: 'Invalid token'}
    )
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
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'phone': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['phone']
        ),
        responses={200: openapi.Response('Reset code sent', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'message': openapi.Schema(type=openapi.TYPE_STRING)})),
                   400: 'Phone required'}
    )
    def post(self, request):
        phone = request.data.get('phone')
        user = get_object_or_404(User, phone=phone)
        # Generate a new password
        new_password = get_random_string(length=10, allowed_chars=string.ascii_letters + string.digits)
        user.set_password(new_password)
        user.save()
        # Use full_name for SMS login, fallback to username
        full_name = f"{user.first_name} {user.last_name}".strip()
        login_name = full_name if full_name else user.username
        try:
            send_sms_via_eskiz(phone, f"aqillimaktab.uz platformasi uchun  login: {login_name} parol: {new_password}")
        except Exception:
            pass
        return Response({'message': 'Password updated and sent via SMS'})

class UsernamePasswordResetSMS(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                'old_password': openapi.Schema(type=openapi.TYPE_STRING),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['phone', 'old_password', 'new_password']
        ),
        responses={200: openapi.Response('Password reset successful', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'message': openapi.Schema(type=openapi.TYPE_STRING)})),
                   400: 'Invalid credentials or password'}
    )
    def post(self, request):
        phone = request.data.get('phone')
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        user = get_object_or_404(User, phone=phone)
        if not user.check_password(old_password):
            return Response({'error': 'Invalid credentials or password'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        # Use full_name for SMS login, fallback to username
        full_name = f"{user.first_name} {user.last_name}".strip()
        login_name = full_name if full_name else user.username
        try:
            send_sms_via_eskiz(phone, f"aqillimaktab.uz platformasi uchun  login: {login_name} parol: {new_password}")
        except Exception:
            pass
        return Response({'message': 'Password reset successful'})
