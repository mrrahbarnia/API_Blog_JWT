"""
Setting up django admin for models.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import (
    User,
    Profile
)


class UserAdmin(UserAdmin):
    """For customizing admin page."""
    ordering = ['id']
    model = User
    list_display = ("email", "is_verified", "is_staff")
    fieldsets = (
        (None, {'fields': ("email", "password")}),
        (_("Permissions"),
            {'fields':
             ("is_active", "is_verified",
              "is_staff", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    readonly_fields = ("last_login",)
    add_fieldsets = (
        (None, {
            "fields": (
                "email",
                "password1",
                "password2",
                "is_active",
                "is_verified",
                "is_staff",
                "is_superuser",
            )
        }),
    )


admin.site.register(User, UserAdmin)
admin.site.register(Profile)
