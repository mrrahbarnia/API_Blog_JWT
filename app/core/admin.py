"""
Setting up django admin for models.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


class UserAdmin(UserAdmin):
    """For customizing admin page."""
    ordering = ['id']
    model = User
    list_display = ("email",)
    fieldsets = (
        (None, {'fields': ("email", "password")}),
        (_("Permissions"),
            {'fields':
             ("is_active", "is_staff", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    readonly_fields = ("last_login",)


admin.site.register(User, UserAdmin)
