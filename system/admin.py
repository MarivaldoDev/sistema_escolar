from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Bimonthly, CustomUser, Grade, Subject, Team


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # Colunas exibidas na lista de usuários
    list_display = (
        "username",
        "registration_number",
        "email",
        "role",
        "is_staff",
        "is_active",
    )

    # Campos visíveis na edição de um usuário
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Informações Pessoais",
            {"fields": ("first_name", "last_name", "email", "date_of_birth")},
        ),  # <-- data de nascimento
        (
            "Permissões",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Informações Extras", {"fields": ("registration_number", "role")}),
        ("Datas Importantes", {"fields": ("last_login", "date_joined")}),
    )

    # Campos visíveis ao criar um novo usuário
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "registration_number",
                    "role",
                    "email",
                    "password1",
                    "password2",
                    "date_of_birth",
                ),
            },
        ),
    )


admin.site.register(Team)
admin.site.register(Subject)
admin.site.register(Grade)
admin.site.register(Bimonthly)
