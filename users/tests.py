from django.urls import reverse
from rest_framework.test import APITestCase
from .models import User

# Create your tests here.

class AuthTests(APITestCase):
    def test_register_sms_send_code(self):
        url = reverse('register-sms-send-code')
        response = self.client.post(url, {'phone': '998901234567'})
        assert response.status_code == 200

    def test_register(self):
        user = User.objects.create(phone='998901234567', username='998901234567')
        from .models import VerificationCode
        VerificationCode.objects.create(user=user, code='123456', purpose='register')
        url = reverse('register')
        response = self.client.post(url, {'phone': '998901234567', 'code': '123456', 'password': 'testpass'})
        assert response.status_code == 200

    def test_login(self):
        user = User.objects.create(phone='998901234567', username='998901234567')
        user.set_password('testpass')
        user.save()
        url = reverse('login')
        response = self.client.post(url, {'phone': '998901234567', 'password': 'testpass'})
        assert response.status_code == 200
