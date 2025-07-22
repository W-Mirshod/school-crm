from django.contrib import admin
from .models import User, VerificationCode, PasswordResetRequest, Class, StudentParent, TeacherClass
from django.contrib.auth.models import Group

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'role', 'phone', 'is_phone_verified', 'is_active', 'is_staff')
    list_filter = ('role', 'is_phone_verified', 'is_active', 'is_staff')
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

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)
    filter_horizontal = ('students',)

@admin.register(StudentParent)
class StudentParentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'parent')
    search_fields = ('student__username', 'parent__username')

@admin.register(TeacherClass)
class TeacherClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'teacher', 'class_obj')
    search_fields = ('teacher__username', 'class_obj__name')

admin.site.unregister(Group)
