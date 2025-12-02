from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Attendance,
    AttendanceRecord,
    Bimonthly,
    CustomUser,
    Grade,
    Subject,
    Team,
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    ordering = ("first_name", "last_name")

    list_display = (
        "first_name",
        "last_name",
        "registration_number",
        "email",
        "role",
        "image_profile",
        "is_staff",
        "is_active",
    )

    fieldsets = (
        (None, {"fields": ("password",)}),
        (
            "Informações Pessoais",
            {"fields": ("first_name", "last_name", "email", "date_of_birth")},
        ),
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
        (
            "Informações Extras",
            {"fields": ("registration_number", "role", "image_profile")},
        ),
        ("Datas Importantes", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "first_name",
                    "last_name",
                    "registration_number",
                    "role",
                    "email",
                    "password1",
                    "password2",
                    "date_of_birth",
                    "image_profile",
                ),
            },
        ),
    )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "year")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if user.role == "professor" and not user.is_superuser:
            return qs.filter(subjects__teacher=user).distinct()
        return qs


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "listar_professores", "listar_turmas")

    def listar_professores(self, obj):
        return ", ".join([t.get_full_name() or t.username for t in obj.teachers.all()])

    listar_professores.short_description = "Professores"

    def listar_turmas(self, obj):
        return ", ".join([t.name for t in obj.team.all()])

    listar_turmas.short_description = "Turmas"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if user.role == "professor" and not user.is_superuser:
            # agora filtra usando ManyToMany
            return qs.filter(teachers=user).distinct()
        return qs

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        user = request.user
        if (
            db_field.name == "teachers"
            and user.role == "professor"
            and not user.is_superuser
        ):
            kwargs["queryset"] = kwargs["queryset"].filter(id=user.id)
        return super().formfield_for_manytomany(db_field, request, **kwargs)


admin.site.register(Grade)
admin.site.register(Bimonthly)
admin.site.register(Attendance)
admin.site.register(AttendanceRecord)
