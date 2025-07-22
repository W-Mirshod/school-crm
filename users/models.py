from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    STUDENT = 'student'
    PARENT = 'parent'
    TEACHER = 'teacher'
    MANAGER = 'manager'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (PARENT, 'Parent'),
        (TEACHER, 'Teacher'),
        (MANAGER, 'Manager'),
        (ADMIN, 'Admin'),
    ]
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default=STUDENT)
    phone = models.CharField(max_length=20, unique=True)
    is_phone_verified = models.BooleanField(default=False)

class VerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    purpose = models.CharField(max_length=32)  # e.g. 'register', 'reset_password'

class PasswordResetRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

class Class(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)

class StudentParent(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_parents')
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parent_students')

class TeacherClass(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teacher_classes')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='class_teachers')
