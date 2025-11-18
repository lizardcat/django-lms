from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model for the LMS with role-based access control.
    """
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        INSTRUCTOR = 'INSTRUCTOR', 'Instructor'
        ADMIN = 'ADMIN', 'Admin'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        help_text="User role in the LMS"
    )
    bio = models.TextField(
        blank=True,
        max_length=500,
        help_text="User biography"
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        help_text="User profile picture"
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text="User's date of birth"
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_instructor(self):
        return self.role == self.Role.INSTRUCTOR

    @property
    def is_admin(self):
        """Admin status is tied to Django's is_superuser flag"""
        return self.is_superuser or self.role == self.Role.ADMIN

    def save(self, *args, **kwargs):
        """Automatically set role to ADMIN for superusers"""
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)
