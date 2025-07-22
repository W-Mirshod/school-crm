from django.urls import path
from .views import RegisterSMSSendCode, Register, Login, RefreshToken, ParolniTiklash, UsernamePasswordResetSMS

urlpatterns = [
    path('register-sms-send-code/', RegisterSMSSendCode.as_view(), name='register-sms-send-code'),
    path('register/', Register.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('refresh-token/', RefreshToken.as_view(), name='refresh-token'),
    path('parolni-tiklash/', ParolniTiklash.as_view(), name='parolni-tiklash'),
    path('username-password-reset-sms/', UsernamePasswordResetSMS.as_view(), name='username-password-reset-sms'),
] 