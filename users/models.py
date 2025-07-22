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

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['id']

class VerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    purpose = models.CharField(max_length=32)  # e.g. 'register', 'reset_password'

    class Meta:
        verbose_name = 'Verification Code'
        verbose_name_plural = 'Verification Codes'
        ordering = ['-created_at']

class PasswordResetRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Password Reset Request'
        verbose_name_plural = 'Password Reset Requests'
        ordering = ['-created_at']

class Class(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    students = models.ManyToManyField('User', related_name='classes', blank=True)

    class Meta:
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'
        ordering = ['name']

class StudentParent(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_parents')
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parent_students')

    class Meta:
        verbose_name = 'Student-Parent Relationship'
        verbose_name_plural = 'Student-Parent Relationships'
        unique_together = ('student', 'parent')

class TeacherClass(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teacher_classes')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='class_teachers')

    class Meta:
        verbose_name = 'Teacher-Class Relationship'
        verbose_name_plural = 'Teacher-Class Relationships'
        unique_together = ('teacher', 'class_obj')
