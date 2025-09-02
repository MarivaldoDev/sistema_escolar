from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ("email", "registration_number", "role")
    list_filter = ("role",)

    fieldsets = (
        (None, {"fields": ("email", "role", "registration_number")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "role"),
        }),
    )

    readonly_fields = ("registration_number",)

    search_fields = ("email", "registration_number")
    ordering = ("email",)
