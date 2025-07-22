from django.urls import path
from .views import RegisterSMSSendCode, Register, Login, RefreshToken, ParolniTiklash, UsernamePasswordResetSMS

urlpatterns = [
    path('register-sms-send-code/', RegisterSMSSendCode.as_view(), name='register-sms-send-code'),
    path('register/', Register.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('refresh-token/', RefreshToken.as_view(), name='refresh-token'),
    path('username-password-reset-sms/', ParolniTiklash.as_view(), name='username-password-reset-sms'),
    path('update-password/', UsernamePasswordResetSMS.as_view(), name='update-password'),
] 