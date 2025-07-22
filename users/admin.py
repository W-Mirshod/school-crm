from django.contrib import admin
from .models import User, VerificationCode, PasswordResetRequest

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'phone', 'is_phone_verified', 'is_active', 'is_staff')
    list_filter = ('is_phone_verified', 'is_active', 'is_staff')
    search_fields = ('username', 'phone')

@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'code', 'purpose', 'created_at')
    list_filter = ('purpose', 'created_at')
    search_fields = ('user__username', 'user__phone', 'code')

@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'code', 'created_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'user__phone', 'code')
