# Generated by Django 5.2.4 on 2025-07-22 14:34

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='class',
            options={'ordering': ['name'], 'verbose_name': 'Class', 'verbose_name_plural': 'Classes'},
        ),
        migrations.AlterModelOptions(
            name='passwordresetrequest',
            options={'ordering': ['-created_at'], 'verbose_name': 'Password Reset Request', 'verbose_name_plural': 'Password Reset Requests'},
        ),
        migrations.AlterModelOptions(
            name='studentparent',
            options={'verbose_name': 'Student-Parent Relationship', 'verbose_name_plural': 'Student-Parent Relationships'},
        ),
        migrations.AlterModelOptions(
            name='teacherclass',
            options={'verbose_name': 'Teacher-Class Relationship', 'verbose_name_plural': 'Teacher-Class Relationships'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['id'], 'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
        migrations.AlterModelOptions(
            name='verificationcode',
            options={'ordering': ['-created_at'], 'verbose_name': 'Verification Code', 'verbose_name_plural': 'Verification Codes'},
        ),
        migrations.AddField(
            model_name='class',
            name='students',
            field=models.ManyToManyField(blank=True, related_name='classes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='studentparent',
            unique_together={('student', 'parent')},
        ),
        migrations.AlterUniqueTogether(
            name='teacherclass',
            unique_together={('teacher', 'class_obj')},
        ),
    ]
